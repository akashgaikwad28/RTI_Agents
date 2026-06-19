"""
api/auth/jwt_handler.py
-----------------------
JWT token creation, decoding, and FastAPI dependency helpers.

Supports:
  - Short-lived access tokens (HS256, 60 min default)
  - Long-lived refresh tokens (7 days default)
  - Role-based access dependency factory
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from config.settings import settings

# ── Token types ───────────────────────────────────────────────────

TokenType = Literal["access", "refresh", "reset"]

_bearer = HTTPBearer(auto_error=False)


# ── Token creation ────────────────────────────────────────────────

def _build_token(
    data: dict[str, Any],
    token_type: TokenType,
    expires_delta: timedelta,
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        **data,
        "iat": now,
        "exp": now + expires_delta,
        "jti": str(uuid.uuid4()),  # Unique token ID (useful for blacklisting)
        "type": token_type,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: str, email: str, role: str, name: str) -> str:
    return _build_token(
        {"sub": user_id, "email": email, "role": role, "name": name},
        "access",
        timedelta(minutes=settings.JWT_ACCESS_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: str) -> str:
    return _build_token(
        {"sub": user_id},
        "refresh",
        timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS),
    )


def create_reset_token(user_id: str, email: str) -> str:
    """Short-lived (30 min) token for password reset flows."""
    return _build_token(
        {"sub": user_id, "email": email},
        "reset",
        timedelta(minutes=30),
    )


# ── Token decoding ────────────────────────────────────────────────

def decode_token(token: str, expected_type: TokenType = "access") -> dict[str, Any]:
    """
    Decode and validate a JWT token.
    Raises HTTP 401 on any validation failure.
    """
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code": "INVALID_TOKEN", "message": "Could not validate credentials."},
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError:
        raise credentials_error

    if payload.get("type") != expected_type:
        raise credentials_error
    if not payload.get("sub"):
        raise credentials_error

    return payload


# ── FastAPI dependencies ───────────────────────────────────────────

async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict[str, Any]:
    """
    FastAPI dependency that extracts and validates the Bearer token.
    Returns the decoded JWT payload (includes sub, email, role, name).
    Raises 401 if token is missing or invalid.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "MISSING_TOKEN", "message": "Authentication token is required."},
            headers={"WWW-Authenticate": "Bearer"},
        )
    return decode_token(credentials.credentials, expected_type="access")


def require_role(*allowed_roles: str):
    """
    FastAPI dependency factory for role-based access control.

    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_role("admin"))])
        @router.post("/officer-action", dependencies=[Depends(require_role("officer", "admin"))])
    """
    async def _checker(user: dict = Depends(get_current_user)) -> dict:
        if user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": f"Access denied. Required roles: {list(allowed_roles)}",
                },
            )
        return user
    return _checker
