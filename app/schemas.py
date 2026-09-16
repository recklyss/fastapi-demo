from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import field_validator


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=1)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    created_at: datetime


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        title = value.strip()
        if not title:
            raise ValueError("title cannot be blank")
        return title


class TodoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    completed: bool | None = None

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str | None) -> str | None:
        if value is None:
            return value
        title = value.strip()
        if not title:
            raise ValueError("title cannot be blank")
        return title


class TodoPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    completed: bool
    created_at: datetime
    updated_at: datetime
