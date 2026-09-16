import hashlib
import uuid
from datetime import UTC
from datetime import datetime
from datetime import timedelta
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlalchemy import select

from app.config import get_settings
from app.db import UnitOfWork
from app.db import get_uow
from app.models import RefreshToken
from app.models import User


password_hasher = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(plain: str) -> str:
    return password_hasher.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return password_hasher.verify(plain, hashed)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_access_token(user_id: str) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    return jwt.encode(
        {
            "sub": user_id,
            "type": "access",
            "jti": str(uuid.uuid4()),
            "exp": now + timedelta(seconds=settings.access_token_ttl_seconds),
            "iat": now,
        },
        settings.secret_key,
        algorithm="HS256",
    )


def create_refresh_token(user_id: str) -> tuple[str, str]:
    settings = get_settings()
    now = datetime.now(UTC)
    jti = str(uuid.uuid4())
    token = jwt.encode(
        {
            "sub": user_id,
            "type": "refresh",
            "jti": jti,
            "exp": now + timedelta(seconds=settings.refresh_token_ttl_seconds),
            "iat": now,
        },
        settings.secret_key,
        algorithm="HS256",
    )
    return token, jti


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, get_settings().secret_key, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


def issue_token_pair(uow: UnitOfWork, user: User) -> dict[str, str]:
    settings = get_settings()
    access = create_access_token(user.id)
    refresh, jti = create_refresh_token(user.id)
    uow.session.add(
        RefreshToken(
            user_id=user.id,
            jti=jti,
            token_hash=hash_refresh_token(refresh),
            expires_at=datetime.now(UTC) + timedelta(seconds=settings.refresh_token_ttl_seconds),
        )
    )
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
    }


def get_refresh_row(uow: UnitOfWork, token: str) -> RefreshToken:
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    result = uow.session.execute(select(RefreshToken).where(RefreshToken.jti == payload.get("jti")))
    row = result.scalar_one_or_none()
    now = datetime.now(UTC)
    if row is None or row.revoked_at is not None or row.expires_at < now or row.token_hash != hash_refresh_token(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return row


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> User:
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    try:
        user_id = str(uuid.UUID(payload["sub"]))
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    result = uow.session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user
