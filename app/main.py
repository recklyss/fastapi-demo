from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from sqlalchemy import text

from app.config import get_settings
from app.db import create_engine_and_factory


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    engine, session_factory = create_engine_and_factory(get_settings())
    app.state.engine = engine
    app.state.session_factory = session_factory
    yield
    engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(title="Todo API", lifespan=lifespan)

    @app.get("/health")
    def health(request: Request) -> dict[str, str]:
        try:
            with request.app.state.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception:
            raise HTTPException(
                status_code=503, detail="database unavailable"
            ) from None
        return {"status": "ok"}

    from app.routers import auth
    from app.routers import todos

    app.include_router(auth.router)
    app.include_router(todos.router)
    return app


app = create_app()
