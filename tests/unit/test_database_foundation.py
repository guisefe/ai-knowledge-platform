from app.infra.database import Base, async_session_factory, engine, get_db_session


def test_database_base_metadata_exists() -> None:
    assert Base.metadata is not None


def test_async_engine_is_configured() -> None:
    assert engine is not None


def test_async_session_factory_is_configured() -> None:
    assert async_session_factory is not None


def test_get_db_session_function_exists() -> None:
    assert callable(get_db_session)
