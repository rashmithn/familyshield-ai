"""Test configuration: temporary SQLite database and dependency override.

Environment variables are set BEFORE importing backend modules so the settings
singleton points at an isolated temporary database.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_TMP_DIR = tempfile.mkdtemp(prefix="familyshield-tests-")
os.environ["DATABASE_URL"] = "sqlite:///" + (Path(_TMP_DIR) / "test.db").as_posix()
os.environ["SECRET_KEY"] = "test-only-secret-key-not-for-production-12345"
os.environ["GROQ_API_KEY"] = ""
os.environ["GOOGLE_SAFE_BROWSING_API_KEY"] = ""
os.environ["SAFE_URL_PROBE"] = "false"
os.environ["DEV_AUTO_CREATE_TABLES"] = "false"
os.environ["RATE_LIMIT_PER_MINUTE"] = "20"

from fastapi.testclient import TestClient  # noqa: E402

from backend.database import Base, SessionLocal, engine  # noqa: E402
from backend.deps import get_db  # noqa: E402
from backend.main import app  # noqa: E402
from backend.models import User  # noqa: E402
from backend.rate_limit import reset_rate_limits  # noqa: E402


@pytest.fixture()
def client():
    from backend import models  # noqa: F401  (ensure metadata is populated)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    reset_rate_limits()

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        reset_rate_limits()


@pytest.fixture()
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
