"""Initial schema: users, families, members, scans, indicators, alerts, notifications.

Revision ID: 0001_initial
Revises: None
Create Date: 2026-11-24
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(150), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "families",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("invite_code", sa.String(32), nullable=False),
        sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("invite_code", name="uq_families_invite_code"),
    )
    op.create_index("ix_families_invite_code", "families", ["invite_code"], unique=True)
    op.create_index("ix_families_created_by", "families", ["created_by"])

    op.create_table(
        "family_members",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("family_id", sa.String(36), sa.ForeignKey("families.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("family_id", "user_id", name="uq_family_member_family_user"),
    )
    op.create_index("ix_family_members_family_id", "family_members", ["family_id"])
    op.create_index("ix_family_members_user_id", "family_members", ["user_id"])
    op.create_index("ix_family_members_family_role", "family_members", ["family_id", "role"])
    op.create_index("ix_family_members_user_family", "family_members", ["user_id", "family_id"])

    op.create_table(
        "scans",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("family_id", sa.String(36), sa.ForeignKey("families.id", ondelete="CASCADE"), nullable=True),
        sa.Column("scan_type", sa.String(16), nullable=False),
        sa.Column("risk_score", sa.Integer(), nullable=False),
        sa.Column("risk_level", sa.String(16), nullable=False),
        sa.Column("category", sa.String(120), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("recommended_actions", sa.JSON(), nullable=False),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("engine", sa.String(32), nullable=False),
        sa.Column("content_excerpt", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_scans_user_id", "scans", ["user_id"])
    op.create_index("ix_scans_family_id", "scans", ["family_id"])
    op.create_index("ix_scans_user_created", "scans", ["user_id", "created_at"])
    op.create_index("ix_scans_family_created", "scans", ["family_id", "created_at"])
    op.create_index("ix_scans_risk_level", "scans", ["risk_level"])
    op.create_index("ix_scans_scan_type", "scans", ["scan_type"])

    op.create_table(
        "scam_indicators",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("scan_id", sa.String(36), sa.ForeignKey("scans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("label", sa.String(150), nullable=False),
        sa.Column("severity", sa.String(16), nullable=False),
        sa.Column("phrase", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
    )
    op.create_index("ix_indicators_scan_id", "scam_indicators", ["scan_id"])
    op.create_index("ix_indicators_scan_code", "scam_indicators", ["scan_id", "code"])

    op.create_table(
        "family_alerts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("family_id", sa.String(36), sa.ForeignKey("families.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scan_id", sa.String(36), sa.ForeignKey("scans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("severity", sa.String(16), nullable=False),
        sa.Column("risk_level", sa.String(16), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.UniqueConstraint("family_id", "scan_id", name="uq_alert_family_scan"),
    )
    op.create_index("ix_alerts_family_id", "family_alerts", ["family_id"])
    op.create_index("ix_alerts_scan_id", "family_alerts", ["scan_id"])
    op.create_index("ix_alerts_family_status", "family_alerts", ["family_id", "status"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("alert_id", sa.String(36), sa.ForeignKey("family_alerts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index("ix_notifications_alert_id", "notifications", ["alert_id"])
    op.create_index("ix_notifications_user_created", "notifications", ["user_id", "created_at"])


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("family_alerts")
    op.drop_table("scam_indicators")
    op.drop_table("scans")
    op.drop_table("family_members")
    op.drop_table("families")
    op.drop_table("users")
