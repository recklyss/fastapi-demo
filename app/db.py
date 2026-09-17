from collections.abc import Generator

from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from app.config import Settings


def create_engine_and_factory(
    settings: Settings,
) -> tuple[Engine, sessionmaker[Session]]:
    engine = create_engine(settings.sqlalchemy_url(), pool_pre_ping=True)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    return engine, session_factory


def get_db(request: Request) -> Generator[Session]:
    session = request.app.state.session_factory()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
