"""Shared FastAPI dependencies and authorization helpers."""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Family, FamilyMember, Scan, User
from backend.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not token:
        raise CREDENTIALS_EXCEPTION
    payload = decode_access_token(token)
    if not payload:
        raise CREDENTIALS_EXCEPTION
    user = db.get(User, payload["sub"])
    if user is None:
        raise CREDENTIALS_EXCEPTION
    return user


def get_user_family_ids(db: Session, user_id: str) -> list[str]:
    rows = db.execute(select(FamilyMember.family_id).where(FamilyMember.user_id == user_id)).all()
    return [row[0] for row in rows]


def get_membership(db: Session, family_id: str, user_id: str) -> FamilyMember | None:
    return db.scalar(
        select(FamilyMember).where(
            FamilyMember.family_id == family_id, FamilyMember.user_id == user_id
        )
    )


def require_family_member(db: Session, family_id: str, user_id: str) -> FamilyMember:
    membership = get_membership(db, family_id, user_id)
    if membership is None:
        # 404 rather than 403 so family existence is not disclosed to outsiders.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")
    return membership


def require_family_admin(db: Session, family_id: str, user_id: str) -> FamilyMember:
    membership = require_family_member(db, family_id, user_id)
    if membership.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only family administrators can perform this action",
        )
    return membership


def accessible_scans(user_id: str, family_ids: list[str]):
    """SELECT of scans visible to a user: their own + scans in their families."""
    conditions = [Scan.user_id == user_id]
    if family_ids:
        conditions.append(Scan.family_id.in_(family_ids))
    return select(Scan).where(or_(*conditions))
