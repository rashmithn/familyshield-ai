"""ORM models.

Privacy rule: this schema stores NO raw OTPs, passwords, banking credentials,
card numbers or other secrets. Only redacted excerpts of user-submitted text
are persisted (see backend/services/redaction.py).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from backend.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now, nullable=False
    )

    family_memberships: Mapped[list[FamilyMember]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    scans: Mapped[list[Scan]] = relationship(
        back_populates="owner", cascade="all, delete-orphan", passive_deletes=True
    )
    reviewed_alerts: Mapped[list[FamilyAlert]] = relationship(
        back_populates="reviewer", foreign_keys="FamilyAlert.reviewed_by"
    )
    notifications: Mapped[list[Notification]] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )
    created_families: Mapped[list[Family]] = relationship(
        back_populates="creator", foreign_keys="Family.created_by"
    )


class Family(Base):
    __tablename__ = "families"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    invite_code: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    created_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)

    creator: Mapped[User | None] = relationship(back_populates="created_families", foreign_keys=[created_by])
    members: Mapped[list[FamilyMember]] = relationship(
        back_populates="family", cascade="all, delete-orphan", passive_deletes=True
    )
    alerts: Mapped[list[FamilyAlert]] = relationship(
        back_populates="family", cascade="all, delete-orphan", passive_deletes=True
    )
    scans: Mapped[list[Scan]] = relationship(
        back_populates="family", cascade="all, delete-orphan", passive_deletes=True
    )


class FamilyMember(Base):
    __tablename__ = "family_members"
    __table_args__ = (
        UniqueConstraint("family_id", "user_id", name="uq_family_member_family_user"),
        Index("ix_family_members_family_role", "family_id", "role"),
        Index("ix_family_members_user_family", "user_id", "family_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    family_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("families.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(16), default="member", nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)

    family: Mapped[Family] = relationship(back_populates="members")
    user: Mapped[User] = relationship(back_populates="family_memberships")


class Scan(Base):
    __tablename__ = "scans"
    __table_args__ = (
        Index("ix_scans_user_created", "user_id", "created_at"),
        Index("ix_scans_family_created", "family_id", "created_at"),
        Index("ix_scans_risk_level", "risk_level"),
        Index("ix_scans_scan_type", "scan_type"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    family_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("families.id", ondelete="CASCADE"), nullable=True
    )
    scan_type: Mapped[str] = mapped_column(String(16), nullable=False)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(16), nullable=False)
    category: Mapped[str] = mapped_column(String(120), nullable=False)
    confidence_score: Mapped[float] = mapped_column(nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    recommended_actions: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    engine: Mapped[str] = mapped_column(String(32), nullable=False)
    content_excerpt: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)

    owner: Mapped[User] = relationship(back_populates="scans")
    family: Mapped[Family | None] = relationship(back_populates="scans")
    indicators: Mapped[list[ScamIndicator]] = relationship(
        back_populates="scan", cascade="all, delete-orphan", passive_deletes=True
    )
    alerts: Mapped[list[FamilyAlert]] = relationship(
        back_populates="scan", cascade="all, delete-orphan", passive_deletes=True
    )


class ScamIndicator(Base):
    __tablename__ = "scam_indicators"
    __table_args__ = (Index("ix_indicators_scan_code", "scan_id", "code"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    scan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    label: Mapped[str] = mapped_column(String(150), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    phrase: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    scan: Mapped[Scan] = relationship(back_populates="indicators")


class FamilyAlert(Base):
    __tablename__ = "family_alerts"
    __table_args__ = (
        UniqueConstraint("family_id", "scan_id", name="uq_alert_family_scan"),
        Index("ix_alerts_family_status", "family_id", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    family_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("families.id", ondelete="CASCADE"), nullable=False
    )
    scan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(16), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="unread", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    family: Mapped[Family] = relationship(back_populates="alerts")
    scan: Mapped[Scan] = relationship(back_populates="alerts")
    reviewer: Mapped[User | None] = relationship(back_populates="reviewed_alerts", foreign_keys=[reviewed_by])


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (Index("ix_notifications_user_created", "user_id", "created_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    alert_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("family_alerts.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)

    user: Mapped[User] = relationship(back_populates="notifications")
