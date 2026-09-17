from typing import Annotated
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Path
from fastapi import status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.models import Todo
from app.models import User
from app.schemas import TodoCreate
from app.schemas import TodoPublic
from app.schemas import TodoUpdate


router = APIRouter(prefix="/todos", tags=["todos"])

TodoId = Annotated[UUID, Path(description="The ID of the todo")]


def _owned_todo(db: Session, user: User, todo_id: UUID) -> Todo:
    result = db.execute(select(Todo).where(Todo.id == str(todo_id), Todo.user_id == user.id))
    todo = result.scalar_one_or_none()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo


@router.get("", response_model=list[TodoPublic])
def list_todos(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[Todo]:
    result = db.execute(select(Todo).where(Todo.user_id == user.id).order_by(Todo.created_at.desc()))
    return list(result.scalars().all())


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TodoPublic)
def create_todo(
    body: TodoCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Todo:
    todo = Todo(user_id=user.id, title=body.title)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


@router.get("/{todo_id}", response_model=TodoPublic)
def get_todo(
    todo_id: TodoId,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Todo:
    return _owned_todo(db, user, todo_id)


@router.patch("/{todo_id}", response_model=TodoPublic)
def update_todo(
    todo_id: TodoId,
    body: TodoUpdate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Todo:
    todo = _owned_todo(db, user, todo_id)
    updates = body.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(todo, field, value)
    db.commit()
    db.refresh(todo)
    return todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: TodoId,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    todo = _owned_todo(db, user, todo_id)
    db.delete(todo)
    db.commit()
