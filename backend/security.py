"""Password hashing and JWT helpers.

bcrypt is used directly (no passlib): passlib's bcrypt backend is unreliable on
Python 3.13 with bcrypt 4.x. Passwords are SHA-256 pre-hashed and base64-encoded
before bcrypt so long passwords and the 72-byte bcrypt limit are handled safely.
"""

from __future__ import annotations

import base64
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from backend.config import settings


def _prehash(password: str) -> bytes:
    digest = hashlib.sha256(password.encode("utf-8")).digest()
    return base64.b64encode(digest)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_prehash(password), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_prehash(password), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    minutes = expires_minutes if expires_minutes is not None else settings.ACCESS_TOKEN_EXPIRE_MINUTES
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=minutes),
        "iss": "familyshield-ai",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Return claims for a valid token, otherwise None (never raises)."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            issuer="familyshield-ai",
            options={"require": ["exp", "sub"]},
        )
    except jwt.PyJWTError:
        return None
    if not isinstance(payload.get("sub"), str) or not payload["sub"]:
        return None
    return payload
