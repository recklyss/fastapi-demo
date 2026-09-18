from datetime import datetime
from datetime import timezone
from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_refresh_row
from app.auth import hash_password
from app.auth import issue_token_pair
from app.auth import verify_password
from app.db import get_db
from app.models import User
from app.schemas import RefreshRequest
from app.schemas import TokenPair
from app.schemas import UserCreate
from app.schemas import UserPublic


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserPublic,
)
def register(body: UserCreate, db: Annotated[Session, Depends(get_db)]) -> User:
    taken = db.execute(select(User).where(User.username == body.username)).scalar_one_or_none()
    if taken is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")
    user = User(username=body.username, password_hash=hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenPair)
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    result = db.execute(select(User).where(User.username == form.username))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(form.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    tokens = issue_token_pair(db, user)
    db.commit()
    return tokens


@router.post("/refresh", response_model=TokenPair)
def refresh(body: RefreshRequest, db: Annotated[Session, Depends(get_db)]) -> dict[str, str]:
    row = get_refresh_row(db, body.refresh_token)
    row.revoked_at = datetime.now(timezone.utc)
    user = db.get(User, row.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    tokens = issue_token_pair(db, user)
    db.commit()
    return tokens


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(body: RefreshRequest, db: Annotated[Session, Depends(get_db)]) -> None:
    row = get_refresh_row(db, body.refresh_token)
    row.revoked_at = datetime.now(timezone.utc)
    db.commit()
