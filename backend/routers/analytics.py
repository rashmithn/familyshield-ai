"""Analytics — every number is computed from database rows."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import accessible_scans, get_current_user, get_user_family_ids
from backend.models import Family, FamilyAlert, FamilyMember, Scan, User
from backend.serializers import serialize_scan

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
def overview(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    family_ids = get_user_family_ids(db, user.id)
    scans = list(
        db.scalars(accessible_scans(user.id, family_ids).order_by(Scan.created_at.desc())).all()
    )
    risk_counts = Counter(scan.risk_level for scan in scans)
    total = len(scans)

    alerts: list[FamilyAlert] = []
    if family_ids:
        alerts = list(db.scalars(select(FamilyAlert).where(FamilyAlert.family_id.in_(family_ids))).all())
    unread = sum(1 for alert in alerts if alert.status == "unread")
    average = round(sum(scan.risk_score for scan in scans) / total) if total else 0

    # Last 7 calendar days including zero days.
    today = datetime.now(timezone.utc).date()
    trend_counts: dict[date, list[int]] = defaultdict(lambda: [0, 0])
    for scan in scans:
        created = scan.created_at
        if created is None:
            continue
        day = created.date() if hasattr(created, "date") else created
        trend_counts[day][0] += 1
        if scan.risk_level == "high_risk":
            trend_counts[day][1] += 1
    weekly_trend = []
    for offset in range(6, -1, -1):
        day = today - timedelta(days=offset)
        scans_day, high_day = trend_counts.get(day, [0, 0])
        weekly_trend.append(
            {"date": day.isoformat(), "label": day.strftime("%a"), "scans": scans_day, "high_risk": high_day}
        )

    category_counts = Counter(scan.category for scan in scans if scan.category)
    categories = [
        {"name": name, "count": count}
        for name, count in sorted(category_counts.items(), key=lambda item: (-item[1], item[0]))
    ]

    risk_distribution = [
        {"name": "Safe", "value": risk_counts.get("safe", 0)},
        {"name": "Suspicious", "value": risk_counts.get("suspicious", 0)},
        {"name": "High Risk", "value": risk_counts.get("high_risk", 0)},
    ]

    family_activity = []
    for family_id in family_ids:
        family = db.get(Family, family_id)
        if family is None:
            continue
        family_scans = [scan for scan in scans if scan.family_id == family_id]
        member_count = db.scalar(
            select(func.count()).select_from(FamilyMember).where(FamilyMember.family_id == family_id)
        ) or 0
        family_activity.append(
            {
                "family_name": family.name,
                "scans": len(family_scans),
                "high_risk": sum(1 for scan in family_scans if scan.risk_level == "high_risk"),
                "members": member_count,
            }
        )
    family_activity.sort(key=lambda item: (-item["scans"], item["family_name"]))

    return {
        "total_scans": total,
        "high_risk": risk_counts.get("high_risk", 0),
        "suspicious": risk_counts.get("suspicious", 0),
        "safe": risk_counts.get("safe", 0),
        "shared_alerts": len(alerts),
        "unread_alerts": unread,
        "average_risk_score": average,
        "weekly_trend": weekly_trend,
        "categories": categories,
        "risk_distribution": risk_distribution,
        "family_activity": family_activity,
        "recent_scans": [serialize_scan(scan) for scan in scans[:5]],
        "scope": "family and personal scans",
    }
