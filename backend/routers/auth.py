"""Authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import get_current_user
from backend.models import User
from backend.schemas import LoginIn, RegisterIn, TokenOut, UpdateUserIn, UserOut
from backend.security import create_access_token, hash_password, verify_password
from backend.serializers import serialize_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterIn, db: Session = Depends(get_db)) -> TokenOut:
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = User(email=payload.email, hashed_password=hash_password(payload.password), full_name=payload.full_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenOut(access_token=create_access_token(user.id), user=serialize_user(db, user))


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)) -> TokenOut:
    user = db.scalar(select(User).where(User.email == payload.email))
    # Same generic error for unknown user and bad password.
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenOut(access_token=create_access_token(user.id), user=serialize_user(db, user))


@router.get("/me", response_model=UserOut)
def read_me(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> UserOut:
    return serialize_user(db, user)


@router.patch("/me", response_model=UserOut)
def update_me(
    payload: UpdateUserIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserOut:
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.email is not None and payload.email != user.email:
        existing = db.scalar(select(User).where(User.email == payload.email))
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        user.email = payload.email
    db.commit()
    db.refresh(user)
    return serialize_user(db, user)
