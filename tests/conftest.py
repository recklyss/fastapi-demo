import os
from collections.abc import Generator

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

load_dotenv()
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-tests-only-32b")

_SKIP_SNOWFLAKE = pytest.mark.skip(
    reason="Set SNOWFLAKE_* env vars (see .env.example) to run tests against Snowflake."
)


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    if os.getenv("SNOWFLAKE_ACCOUNT"):
        return
    for item in items:
        item.add_marker(_SKIP_SNOWFLAKE)


def _truncate() -> None:
    from sqlalchemy import create_engine

    from app.config import get_settings
    from app.models import Base

    engine = create_engine(get_settings().sqlalchemy_url())
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
    engine.dispose()


@pytest.fixture
def client() -> Generator[TestClient]:
    from app.config import get_settings
    from app.main import create_app

    get_settings.cache_clear()
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client
    _truncate()
