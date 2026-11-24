"""Create tables for local SQLite development without Alembic.

Usage from project root:  python -m database.init_db
Production should use:    alembic -c backend/alembic.ini upgrade head
"""

from __future__ import annotations

from sqlalchemy import create_engine

from backend import models  # noqa: F401
from backend.config import settings
from backend.database import Base


def main() -> None:
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(engine)
    print(f"Created/verified tables for the {settings.DATABASE_URL.split('://')[0]} database.")
    if settings.using_dev_database:
        print("WARNING: using the local SQLite development fallback database.")
    engine.dispose()


if __name__ == "__main__":
    main()
