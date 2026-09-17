from types import SimpleNamespace
from unittest.mock import Mock

from app.db import get_db


def test_get_db_rolls_back_and_closes_session() -> None:
    session = Mock()
    session_factory = Mock(return_value=session)
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(session_factory=session_factory)))

    dependency = get_db(request)  # type: ignore[arg-type]
    db = next(dependency)
    dependency.close()

    assert db is session
    session_factory.assert_called_once_with()
    session.rollback.assert_called_once_with()
    session.close.assert_called_once_with()
