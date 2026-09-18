from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.auth import hash_password
from app.db import get_db
from app.models import User
from app.schemas import ResetPasswordRequest
from app.schemas import UserPublic


router = APIRouter(prefix="/user", tags=["user"])


@router.get("/me", response_model=UserPublic)
def me(user: Annotated[User, Depends(get_current_user)]) -> User:
    return user


@router.patch("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
def reset_password(
    body: ResetPasswordRequest,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> None:
    user.password_hash = hash_password(body.new_password)
    db.commit()
