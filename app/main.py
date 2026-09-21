from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.config import get_settings
from app.db import create_engine_and_factory


STATIC_DIR = Path(__file__).resolve().parents[1] / "static"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    engine, session_factory = create_engine_and_factory(get_settings())
    app.state.engine = engine
    app.state.session_factory = session_factory
    yield
    engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(title="Todo API", lifespan=lifespan)
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

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
    from app.routers import pages
    from app.routers import todos
    from app.routers import user

    app.include_router(pages.router)
    app.include_router(auth.router)
    app.include_router(todos.router)
    app.include_router(user.router)
    return app


app = create_app()
