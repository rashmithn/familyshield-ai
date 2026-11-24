"""Personal notifications (extra endpoint, not in the core contract)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import get_current_user
from backend.models import Notification, User
from backend.schemas import NotificationOut

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationOut])
def list_notifications(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[NotificationOut]:
    rows = db.scalars(
        select(Notification).where(Notification.user_id == user.id).order_by(Notification.created_at.desc())
    ).all()
    return [NotificationOut.model_validate(row) for row in rows]
