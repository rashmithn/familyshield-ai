"""Scan creation, listing, detail, deletion and sharing."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import accessible_scans, get_current_user, get_user_family_ids, require_family_member
from backend.models import FamilyAlert, Scan, User
from backend.rate_limit import rate_limiter_dependency
from backend.schemas import MessageResponse, ScanListOut, ScanMessageIn, ScanOut, ScanUrlIn, ShareIn
from backend.serializers import serialize_alert, serialize_scan
from backend.services.scan_service import create_family_alert, run_message_scan, run_url_scan

router = APIRouter(tags=["scans"])


@router.post("/scan/message", response_model=ScanOut, status_code=status.HTTP_201_CREATED)
def scan_message(
    payload: ScanMessageIn,
    user: User = Depends(rate_limiter_dependency),
    db: Session = Depends(get_db),
) -> ScanOut:
    scan = run_message_scan(db, user, payload.text, str(payload.family_id) if payload.family_id else None)
    return serialize_scan(scan)


@router.post("/scan/url", response_model=ScanOut, status_code=status.HTTP_201_CREATED)
def scan_url(
    payload: ScanUrlIn,
    user: User = Depends(rate_limiter_dependency),
    db: Session = Depends(get_db),
) -> ScanOut:
    scan = run_url_scan(db, user, payload.url, str(payload.family_id) if payload.family_id else None)
    return serialize_scan(scan)


@router.get("/scans", response_model=ScanListOut)
def list_scans(
    risk_level: Literal["safe", "suspicious", "high_risk"] | None = None,
    scan_type: Literal["message", "url"] | None = None,
    search: str | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ScanListOut:
    stmt = accessible_scans(user.id, get_user_family_ids(db, user.id))
    if risk_level:
        stmt = stmt.where(Scan.risk_level == risk_level)
    if scan_type:
        stmt = stmt.where(Scan.scan_type == scan_type)
    if search and search.strip():
        pattern = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(Scan.summary.ilike(pattern), Scan.category.ilike(pattern), Scan.content_excerpt.ilike(pattern))
        )
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    scans = db.scalars(stmt.order_by(Scan.created_at.desc()).offset(offset).limit(limit)).all()
    return ScanListOut(items=[serialize_scan(scan) for scan in scans], total=total, limit=limit, offset=offset)


def _get_visible_scan(db: Session, scan_id: str, user: User) -> Scan:
    stmt = accessible_scans(user.id, get_user_family_ids(db, user.id)).where(Scan.id == scan_id)
    scan = db.scalar(stmt)
    if scan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
    return scan


@router.get("/scans/{scan_id}", response_model=ScanOut)
def get_scan(scan_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ScanOut:
    return serialize_scan(_get_visible_scan(db, scan_id, user))


@router.delete("/scans/{scan_id}", response_model=MessageResponse)
def delete_scan(scan_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> MessageResponse:
    scan = _get_visible_scan(db, scan_id, user)
    if scan.user_id != user.id:
        # Only the creator can delete; family admins can review but not delete
        # someone else's scan. Deleting cascades indicators, alerts and notifications.
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the scan owner can delete this scan")
    db.delete(scan)
    db.commit()
    return MessageResponse(message="Scan deleted")


@router.post("/scans/{scan_id}/share")
def share_scan(
    scan_id: str,
    payload: ShareIn | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scan = _get_visible_scan(db, scan_id, user)
    family_id = str(payload.family_id) if payload and payload.family_id else scan.family_id
    if not family_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide family_id to share this scan",
        )
    require_family_member(db, family_id, user.id)
    alert = create_family_alert(db, scan, family_id)
    db.commit()
    db.refresh(alert)
    return {"alert": serialize_alert(alert)}
