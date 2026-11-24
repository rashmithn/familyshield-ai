"""SQLAlchemy 2.x engine/session setup."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.config import settings


class Base(DeclarativeBase):
    """Declarative base for every ORM model."""


def _engine_kwargs(url: str) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        "pool_pre_ping": True,
        "echo": False,  # never echo SQL: it can contain message content
    }
    if url.startswith("sqlite"):
        # File/SQLite connections on Windows need check_same_thread=False for
        # TestClient / FastAPI's threadpool.
        kwargs["connect_args"] = {"check_same_thread": False, "timeout": 30}
    return kwargs


engine = create_engine(settings.DATABASE_URL, **_engine_kwargs(settings.DATABASE_URL))


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection: Any, _connection: Any) -> None:
    """Enable FK enforcement in SQLite (off by default)."""
    try:
        if engine.url.get_backend_name() == "sqlite":
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    except Exception:
        # Some DBAPI drivers do not support PRAGMA; ignore rather than crash.
        return


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a session and always closing it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """Create all tables (local development / tests only)."""
    from backend import models  # noqa: F401  (registers models on Base.metadata)

    Base.metadata.create_all(bind=engine)
