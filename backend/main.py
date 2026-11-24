"""FamilyShield AI FastAPI application entrypoint.

Run locally:  uvicorn backend.main:app --reload
Docs:         /docs
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend import models  # noqa: F401  (registers ORM models)
from backend.config import settings
from backend.database import create_tables
from backend.routers import alerts, analytics, awareness, auth, families, notifications, scans

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings.log_safety_warnings()
    if settings.DEV_AUTO_CREATE_TABLES:
        create_tables()  # local SQLite dev only; production uses `alembic upgrade head`
    yield


app = FastAPI(
    title="FamilyShield AI",
    version="1.0.0",
    description="Family safety scanning API. Analysis is indicative only, never a guarantee.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(families.router)
app.include_router(scans.router)
app.include_router(alerts.router)
app.include_router(analytics.router)
app.include_router(awareness.router)
app.include_router(notifications.router)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "familyshield-ai"}


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    # Log only the exception type: user-submitted text must never appear in logs.
    logger.error("Unhandled error: %s", type(exc).__name__)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
