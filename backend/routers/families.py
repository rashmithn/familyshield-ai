"""Family groups, membership and invite codes."""

from __future__ import annotations

import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.deps import get_current_user, require_family_admin, require_family_member
from backend.models import Family, FamilyMember, User
from backend.schemas import FamilyCreateIn, FamilyMemberOut, FamilyOut, InviteOut, JoinFamilyIn, MemberRoleIn
from backend.serializers import serialize_family, serialize_member

router = APIRouter(prefix="/families", tags=["families"])


def _new_invite_code(db: Session) -> str:
    for _ in range(10):
        code = f"FS-{secrets.token_hex(4).upper()}"
        if not db.scalar(select(Family).where(Family.invite_code == code)):
            return code
    raise HTTPException(status_code=500, detail="Could not generate invite code")


@router.post("", response_model=FamilyOut, status_code=status.HTTP_201_CREATED)
def create_family(payload: FamilyCreateIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> FamilyOut:
    family = Family(
        name=payload.name,
        description=payload.description,
        invite_code=_new_invite_code(db),
        created_by=user.id,
    )
    family.members.append(FamilyMember(user_id=user.id, role="admin"))
    db.add(family)
    db.commit()
    db.refresh(family)
    return serialize_family(db, family, user.id)


@router.get("", response_model=list[FamilyOut])
def list_families(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[FamilyOut]:
    families = db.scalars(
        select(Family)
        .join(FamilyMember, FamilyMember.family_id == Family.id)
        .where(FamilyMember.user_id == user.id)
        .order_by(Family.created_at.desc())
    ).all()
    return [serialize_family(db, family, user.id) for family in families]


@router.post("/join", response_model=FamilyOut)
def join_family(payload: JoinFamilyIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> FamilyOut:
    family = db.scalar(select(Family).where(Family.invite_code == payload.invite_code))
    if family is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite code not found")
    if any(member.user_id == user.id for member in family.members):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already a member of this family")
    family.members.append(FamilyMember(user_id=user.id, role="member"))
    db.commit()
    db.refresh(family)
    return serialize_family(db, family, user.id)


@router.get("/{family_id}", response_model=FamilyOut)
def get_family(family_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> FamilyOut:
    require_family_member(db, family_id, user.id)
    family = db.get(Family, family_id)
    if family is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")
    return serialize_family(db, family, user.id)


@router.patch("/{family_id}/members/{member_id}", response_model=FamilyMemberOut)
def update_member_role(
    family_id: str,
    member_id: str,
    payload: MemberRoleIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FamilyMemberOut:
    require_family_admin(db, family_id, user.id)
    member = db.scalar(
        select(FamilyMember).where(FamilyMember.id == member_id, FamilyMember.family_id == family_id)
    )
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    if member.role == "admin" and payload.role == "member":
        admin_count = db.scalar(
            select(func.count()).select_from(FamilyMember).where(
                FamilyMember.family_id == family_id, FamilyMember.role == "admin"
            )
        )
        if admin_count is not None and admin_count <= 1:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A family must keep at least one admin")
    member.role = payload.role
    db.commit()
    db.refresh(member)
    return serialize_member(member)


@router.post("/{family_id}/invites", response_model=InviteOut)
def rotate_invite(
    family_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InviteOut:
    require_family_admin(db, family_id, user.id)
    family = db.get(Family, family_id)
    if family is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family not found")
    family.invite_code = _new_invite_code(db)
    db.commit()
    db.refresh(family)
    return InviteOut(
        invite_code=family.invite_code,
        invite_url=f"{settings.FRONTEND_BASE_URL.rstrip('/')}/families/join?invite_code={family.invite_code}",
    )
