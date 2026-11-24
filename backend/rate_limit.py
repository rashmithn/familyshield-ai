"""Simple in-memory sliding-window rate limiter for scan endpoints.

Keyed by authenticated user id + endpoint. In-memory state is per process; a
distributed deployment should swap this for Redis. No user content is logged.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque

from fastapi import Depends, HTTPException, Request, status

from backend.config import settings
from backend.deps import get_current_user
from backend.models import User

_windows: dict[tuple[str, str], deque[float]] = defaultdict(deque)
_lock = threading.Lock()


def reset_rate_limits() -> None:
    """Clear all windows (used by tests)."""
    with _lock:
        _windows.clear()


def check_rate_limit(key: str, limit: int | None = None) -> None:
    max_calls = limit if limit is not None else settings.RATE_LIMIT_PER_MINUTE
    now = time.monotonic()
    cutoff = now - 60.0
    with _lock:
        window = _windows[key]
        while window and window[0] <= cutoff:
            window.popleft()
        if len(window) >= max_calls:
            retry_after = max(1, int(window[0] + 60.0 - now) + 1)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {max_calls} scans per minute. Try again shortly.",
                headers={"Retry-After": str(retry_after)},
            )
        window.append(now)


def rate_limiter_dependency(
    request: Request,
    user: User = Depends(get_current_user),
) -> User:
    """Authenticate and apply a per-user, per-endpoint sliding window."""
    check_rate_limit(f"user:{user.id}:{request.url.path}")
    return user
