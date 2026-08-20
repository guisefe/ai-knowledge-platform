from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.database import Base, async_session_factory, engine, get_db_session


def test_database_base_metadata_exists() -> None:
    assert Base.metadata is not None


def test_async_engine_is_configured() -> None:
    assert engine is not None


def test_async_session_factory_is_configured() -> None:
    assert async_session_factory is not None


def test_get_db_session_returns_async_generator() -> None:
    session_generator = get_db_session()

    assert isinstance(session_generator, AsyncGenerator)
    assert session_generator.__name__ == "get_db_session"
