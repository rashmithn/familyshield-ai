"""Family alerts and review workflow."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import get_current_user, get_user_family_ids, require_family_member
from backend.models import FamilyAlert, User
from backend.schemas import AlertOut
from backend.serializers import serialize_alert

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertOut])
def list_alerts(
    status_filter: Literal["all", "unread", "reviewed"] = Query(default="all", alias="status"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AlertOut]:
    family_ids = get_user_family_ids(db, user.id)
    if not family_ids:
        return []
    stmt = select(FamilyAlert).where(FamilyAlert.family_id.in_(family_ids))
    if status_filter == "unread":
        stmt = stmt.where(FamilyAlert.status == "unread")
    elif status_filter == "reviewed":
        stmt = stmt.where(FamilyAlert.status == "reviewed")
    alerts = db.scalars(stmt.order_by(FamilyAlert.created_at.desc())).all()
    return [serialize_alert(alert) for alert in alerts]


@router.post("/{alert_id}/review", response_model=AlertOut)
def review_alert(
    alert_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AlertOut:
    alert = db.get(FamilyAlert, alert_id)
    if alert is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    require_family_member(db, alert.family_id, user.id)
    alert.status = "reviewed"
    alert.reviewed_at = datetime.now(timezone.utc)
    alert.reviewed_by = user.id
    db.commit()
    db.refresh(alert)
    return serialize_alert(alert)
