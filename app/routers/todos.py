from typing import Annotated
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Path
from fastapi import status
from sqlalchemy import select

from app.auth import get_current_user
from app.db import UnitOfWork
from app.db import get_uow
from app.models import Todo
from app.models import User
from app.schemas import TodoCreate
from app.schemas import TodoPublic
from app.schemas import TodoUpdate


router = APIRouter(prefix="/todos", tags=["todos"])

TodoId = Annotated[UUID, Path(description="The ID of the todo")]


def _owned_todo(uow: UnitOfWork, user: User, todo_id: UUID) -> Todo:
    result = uow.session.execute(select(Todo).where(Todo.id == str(todo_id), Todo.user_id == user.id))
    todo = result.scalar_one_or_none()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo


@router.get("", response_model=list[TodoPublic])
def list_todos(
    user: Annotated[User, Depends(get_current_user)],
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> list[Todo]:
    result = uow.session.execute(select(Todo).where(Todo.user_id == user.id).order_by(Todo.created_at.desc()))
    return list(result.scalars().all())


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TodoPublic)
def create_todo(
    body: TodoCreate,
    user: Annotated[User, Depends(get_current_user)],
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> Todo:
    todo = Todo(user_id=user.id, title=body.title)
    uow.session.add(todo)
    uow.commit()
    uow.session.refresh(todo)
    return todo


@router.get("/{todo_id}", response_model=TodoPublic)
def get_todo(
    todo_id: TodoId,
    user: Annotated[User, Depends(get_current_user)],
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> Todo:
    return _owned_todo(uow, user, todo_id)


@router.patch("/{todo_id}", response_model=TodoPublic)
def update_todo(
    todo_id: TodoId,
    body: TodoUpdate,
    user: Annotated[User, Depends(get_current_user)],
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> Todo:
    todo = _owned_todo(uow, user, todo_id)
    updates = body.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(todo, field, value)
    uow.commit()
    uow.session.refresh(todo)
    return todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: TodoId,
    user: Annotated[User, Depends(get_current_user)],
    uow: Annotated[UnitOfWork, Depends(get_uow)],
) -> None:
    todo = _owned_todo(uow, user, todo_id)
    uow.session.delete(todo)
    uow.commit()
