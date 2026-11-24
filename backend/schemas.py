"""Pydantic v2 request/response models matching docs/API_CONTRACT.md exactly."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_serializer, field_validator


def iso(value: datetime | None) -> str | None:
    """Render datetimes as ISO-8601 UTC strings ending in Z."""
    if value is None:
        return None
    if value.tzinfo is None:
        # SQLite drops tzinfo; values written by this app are always UTC.
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class _Out(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------------------------------- auth
class FamilySummary(BaseModel):
    id: str
    name: str
    role: str
    member_count: int


class UserOut(_Out):
    id: str
    email: EmailStr
    full_name: str
    created_at: datetime
    families: list[FamilySummary] = Field(default_factory=list)

    @field_serializer("created_at")
    def _created_at(self, value: datetime) -> str:
        return iso(value)  # type: ignore[return-value]


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=150)

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, value: str) -> str:
        return str(value).strip().lower()

    @field_validator("full_name")
    @classmethod
    def _strip_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("full_name must not be blank")
        return value

    @field_validator("password")
    @classmethod
    def _password_strength(cls, value: str) -> str:
        if not re.search(r"[A-Za-z]", value) or not re.search(r"\d", value):
            raise ValueError("password must contain at least one letter and one number")
        return value


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, value: str) -> str:
        return str(value).strip().lower()


class UpdateUserIn(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=150)
    email: EmailStr | None = None

    @field_validator("full_name")
    @classmethod
    def _strip_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("full_name must not be blank")
        return value

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, value: str | None) -> str | None:
        return str(value).strip().lower() if value else None


class TokenOut(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    user: UserOut


# ------------------------------------------------------------------------ families
class FamilyCreateIn(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=500)

    @field_validator("name")
    @classmethod
    def _strip_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("name must not be blank")
        return value


class JoinFamilyIn(BaseModel):
    invite_code: str = Field(min_length=4, max_length=64)

    @field_validator("invite_code")
    @classmethod
    def _normalize_code(cls, value: str) -> str:
        return value.strip().upper()


class MemberRoleIn(BaseModel):
    role: Literal["admin", "member"]


class FamilyMemberOut(_Out):
    id: str
    user_id: str
    full_name: str
    email: str
    role: str
    joined_at: datetime

    @field_serializer("joined_at")
    def _joined_at(self, value: datetime) -> str:
        return iso(value)  # type: ignore[return-value]


class FamilyOut(_Out):
    id: str
    name: str
    description: str | None
    invite_code: str
    created_at: datetime
    my_role: str
    members: list[FamilyMemberOut]

    @field_serializer("created_at")
    def _created_at(self, value: datetime) -> str:
        return iso(value)  # type: ignore[return-value]


class InviteOut(BaseModel):
    invite_code: str
    invite_url: str


# -------------------------------------------------------------------------- scans
class ScanMessageIn(BaseModel):
    text: str = Field(min_length=1, max_length=20000)
    family_id: UUID | None = None

    @field_validator("text")
    @classmethod
    def _nonblank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text must not be blank")
        return value


class ScanUrlIn(BaseModel):
    url: str = Field(min_length=1, max_length=2048)
    family_id: UUID | None = None

    @field_validator("url")
    @classmethod
    def _nonblank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("url must not be blank")
        return value.strip()


class IndicatorOut(BaseModel):
    code: str
    label: str
    severity: Literal["low", "medium", "high"]
    phrase: str
    description: str


class ScanOut(_Out):
    id: str
    scan_type: str
    risk_score: int
    risk_level: str
    category: str
    confidence_score: float
    summary: str
    explanation: str
    indicators: list[IndicatorOut]
    recommended_actions: list[str]
    details: dict[str, Any]
    engine: str
    content_excerpt: str
    created_at: datetime
    family_id: str | None
    is_shared: bool

    @field_serializer("created_at")
    def _created_at(self, value: datetime) -> str:
        return iso(value)  # type: ignore[return-value]


class ScanListOut(BaseModel):
    items: list[ScanOut]
    total: int
    limit: int
    offset: int


class ShareIn(BaseModel):
    family_id: UUID | None = None


# ------------------------------------------------------------------------- alerts
class AlertOut(_Out):
    id: str
    family_id: str
    family_name: str
    scan_id: str
    title: str
    severity: str
    risk_level: str
    summary: str
    status: str
    created_at: datetime
    reviewed_at: datetime | None
    reviewed_by: str | None
    scan: ScanOut | None = None

    @field_serializer("created_at", "reviewed_at")
    def _dates(self, value: datetime | None) -> str | None:
        return iso(value)  # type: ignore[return-value]


class NotificationOut(_Out):
    id: str
    title: str
    body: str
    is_read: bool
    created_at: datetime
    alert_id: str | None = None

    @field_serializer("created_at")
    def _created_at(self, value: datetime) -> str:
        return iso(value)  # type: ignore[return-value]


class MessageResponse(BaseModel):
    message: str
