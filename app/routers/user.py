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
from app.schemas import UserUpdate


router = APIRouter(prefix="/user", tags=["user"])


@router.get("/me", response_model=UserPublic)
def me(user: Annotated[User, Depends(get_current_user)]) -> User:
    return user


@router.patch("/profile", response_model=UserPublic)
def update_profile(
    body: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    if body.full_name is not None:
        user.full_name = body.full_name
    if body.age is not None:
        user.age = body.age
    db.commit()
    db.refresh(user)
    return user


@router.patch("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
def reset_password(
    body: ResetPasswordRequest,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> None:
    user.password_hash = hash_password(body.new_password)
    db.commit()
