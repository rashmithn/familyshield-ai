"""ORM -> contract-shaped Pydantic conversion helpers."""

from __future__ import annotations

from sqlalchemy.orm import Session

from backend.models import Family, FamilyAlert, FamilyMember, Scan, User
from backend.schemas import (
    AlertOut,
    FamilyMemberOut,
    FamilyOut,
    FamilySummary,
    IndicatorOut,
    ScanOut,
    UserOut,
)


def serialize_user(db: Session, user: User) -> UserOut:
    memberships = (
        db.query(FamilyMember).filter(FamilyMember.user_id == user.id).all()
    )
    families: list[FamilySummary] = []
    for membership in memberships:
        family = db.get(Family, membership.family_id)
        if family is None:
            continue
        member_count = (
            db.query(FamilyMember).filter(FamilyMember.family_id == family.id).count()
        )
        families.append(
            FamilySummary(id=family.id, name=family.name, role=membership.role, member_count=member_count)
        )
    return UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        created_at=user.created_at,
        families=families,
    )


def serialize_member(member: FamilyMember) -> FamilyMemberOut:
    user = member.user
    return FamilyMemberOut(
        id=member.id,
        user_id=member.user_id,
        full_name=user.full_name if user else "Unknown",
        email=user.email if user else "",
        role=member.role,
        joined_at=member.joined_at,
    )


def serialize_family(db: Session, family: Family, viewer_id: str) -> FamilyOut:
    my_role = "member"
    for membership in family.members:
        if membership.user_id == viewer_id:
            my_role = membership.role
            break
    members = [serialize_member(m) for m in sorted(family.members, key=lambda m: m.joined_at)]
    return FamilyOut(
        id=family.id,
        name=family.name,
        description=family.description,
        invite_code=family.invite_code,
        created_at=family.created_at,
        my_role=my_role,
        members=members,
    )


def serialize_scan(scan: Scan) -> ScanOut:
    indicators = [
        IndicatorOut(
            code=i.code,
            label=i.label,
            severity=i.severity,
            phrase=i.phrase,
            description=i.description,
        )
        for i in sorted(scan.indicators, key=lambda i: ({"high": 0, "medium": 1, "low": 2}.get(i.severity, 3), i.code))
    ]
    return ScanOut(
        id=scan.id,
        scan_type=scan.scan_type,
        risk_score=scan.risk_score,
        risk_level=scan.risk_level,
        category=scan.category,
        confidence_score=scan.confidence_score,
        summary=scan.summary,
        explanation=scan.explanation,
        indicators=indicators,
        recommended_actions=list(scan.recommended_actions or []),
        details=dict(scan.details or {}),
        engine=scan.engine,
        content_excerpt=scan.content_excerpt,
        created_at=scan.created_at,
        family_id=scan.family_id,
        is_shared=bool(scan.alerts),
    )


def serialize_alert(alert: FamilyAlert) -> AlertOut:
    family = alert.family
    return AlertOut(
        id=alert.id,
        family_id=alert.family_id,
        family_name=family.name if family else "Family",
        scan_id=alert.scan_id,
        title=alert.title,
        severity=alert.severity,
        risk_level=alert.risk_level,
        summary=alert.summary,
        status=alert.status,
        created_at=alert.created_at,
        reviewed_at=alert.reviewed_at,
        reviewed_by=alert.reviewed_by,
        scan=serialize_scan(alert.scan) if alert.scan else None,
    )
