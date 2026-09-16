from types import SimpleNamespace
from unittest.mock import Mock

from app.db import UnitOfWork
from app.db import get_uow


def test_unit_of_work_delegates_transaction_control() -> None:
    session = Mock()
    session_factory = Mock(return_value=session)

    uow = UnitOfWork(session_factory)
    uow.commit()
    uow.rollback()
    uow.close()

    session_factory.assert_called_once_with()
    session.commit.assert_called_once_with()
    session.rollback.assert_called_once_with()
    session.close.assert_called_once_with()


def test_get_uow_rolls_back_and_closes_session() -> None:
    session = Mock()
    session_factory = Mock(return_value=session)
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(session_factory=session_factory)))

    dependency = get_uow(request)  # type: ignore[arg-type]
    uow = next(dependency)
    dependency.close()

    assert uow.session is session
    session.rollback.assert_called_once_with()
    session.close.assert_called_once_with()
