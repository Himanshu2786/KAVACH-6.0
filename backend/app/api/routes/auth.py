"""
KAVACH 6.0 — Multi-User Authentication & Authorization Router
Enforces secure login, session verification, user role introspection, and team account provisioning.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.models import User
from backend.app.core.security import (
    verify_password,
    create_access_token,
    require_admin,
    hash_password,
)
from backend.app.core.auth import get_current_user
from backend.app.core.time import ist_formatted

router = APIRouter(prefix="/auth", tags=["Authentication & Team Access"])


class LoginRequest(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    user_id: Optional[str] = None
    role: str
    full_name: str
    is_active: bool
    created_at: str


class LoginResponse(BaseModel):
    success: bool
    token: str
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """Authenticate user with User ID / Username and Password."""
    ident = (req.user_id or req.username or "").strip().upper()
    if not ident:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID or Username is required"
        )
    if not req.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is required"
        )

    # Search for user by ID, Username, or legacy user_id
    user = db.query(User).filter(
        (User.id == ident) | 
        (User.id == f"USR-{ident}") |
        (User.username == ident) |
        (User.user_id == ident)
    ).first()

    if not user:
        # Fallback check lowercase/exact
        user = db.query(User).filter(
            (User.id == req.user_id) | 
            (User.username == req.username) |
            (User.user_id == req.user_id)
        ).first()

    target_hash = (getattr(user, "hashed_password", None) or getattr(user, "password_hash", None)) if user else None
    if not user or not target_hash or not verify_password(req.password, target_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid USER ID or password. Please verify your credentials."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated. Contact your security administrator."
        )

    if req.user_id and not req.username:
        effective_role = "DEVELOPER_OWNER" if user.role in ("admin", "DEVELOPER_OWNER", "ADMIN") else "TEAM_USER"
    elif req.username and not req.user_id:
        effective_role = "admin" if user.role in ("admin", "DEVELOPER_OWNER", "ADMIN") else "team_member"
    else:
        effective_role = user.role

    token = create_access_token({
        "sub": user.id,
        "username": user.username,
        "role": effective_role,
        "full_name": user.full_name
    })

    return {
        "success": True,
        "token": token,
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username or user.user_id or user.id,
            "user_id": user.user_id or user.username or user.id,
            "role": effective_role,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "created_at": user.created_at or ist_formatted()
        }
    }


@router.get("/me")
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Retrieve the current authenticated user identity and role."""
    user_payload = {
        "id": current_user.id,
        "username": current_user.username or current_user.user_id or current_user.id,
        "user_id": current_user.user_id or current_user.username or current_user.id,
        "role": current_user.role,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at
    }
    return {
        "success": True,
        **user_payload,
        "user": user_payload
    }


@router.post("/logout")
def logout(response: Response):
    """Terminate the active session and clear authentication cookies."""
    response.delete_cookie(key="access_token")
    return {
        "success": True,
        "message": "Successfully logged out from KAVACH 6.0"
    }


@router.get("/users")
def list_team_users(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """List all registered team accounts and authorization tiers (Admin Only)."""
    users = db.query(User).all()
    return {
        "success": True,
        "count": len(users),
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "role": u.role,
                "full_name": u.full_name,
                "is_active": u.is_active,
                "created_at": u.created_at
            }
            for u in users
        ]
    }
