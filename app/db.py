from collections.abc import Generator

from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from app.config import Settings


class UnitOfWork:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self.session = session_factory()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

    def close(self) -> None:
        self.session.close()


def create_engine_and_factory(
    settings: Settings,
) -> tuple[Engine, sessionmaker[Session]]:
    engine = create_engine(settings.sqlalchemy_url(), pool_pre_ping=True)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    return engine, session_factory


def get_uow(request: Request) -> Generator[UnitOfWork]:
    uow = UnitOfWork(request.app.state.session_factory)
    try:
        yield uow
    finally:
        uow.rollback()
        uow.close()
