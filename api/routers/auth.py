"""
api/routers/auth.py
--------------------
Full authentication router for RTI-Agent.

Endpoints:
  POST /auth/register          – citizen or officer registration
  POST /auth/login             – email + password → JWT pair
  POST /auth/refresh           – refresh token → new access token
  POST /auth/logout            – revoke refresh token
  GET  /auth/me                – current user profile
  POST /auth/change-password   – update password (requires auth)
  POST /auth/forgot-password   – send reset email
  POST /auth/reset-password    – apply password reset

Roles: citizen | officer | admin
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field, model_validator

from api.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    create_reset_token,
    decode_token,
    get_current_user,
)
from api.auth.password import hash_password, verify_password
from mcp_clients.mongo_client import get_mongo_client
from observability.logger import get_logger

logger = get_logger("auth")
router = APIRouter(prefix="/auth", tags=["Authentication"])
_bearer = HTTPBearer(auto_error=False)


# ── Request / Response Schemas ────────────────────────────────────

UserRole = Literal["citizen", "officer", "admin"]

DEPARTMENTS = [
    "agriculture", "road-transport", "education",
    "health", "municipal", "general",
]


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    confirm_password: str = Field(..., min_length=6, max_length=100)
    role: UserRole = "citizen"
    department: Optional[str] = None  # Required for officer role
    phone: Optional[str] = None
    language: Literal["en", "hi", "mr"] = "en"

    @model_validator(mode="after")
    def validate_passwords_and_department(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        if self.role == "officer" and not self.department:
            raise ValueError("Department is required for officer registration.")
        # Prevent self-registration as admin (admins are seeded/assigned)
        if self.role == "admin":
            raise ValueError("Admin accounts cannot be self-registered.")
        return self


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)
    confirm_password: str

    @model_validator(mode="after")
    def validate_passwords(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        return self


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)
    confirm_password: str

    @model_validator(mode="after")
    def validate_passwords(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        return self


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    department: Optional[str] = None
    phone: Optional[str] = None
    language: str
    created_at: str


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    user: UserResponse


# ── Helpers ───────────────────────────────────────────────────────

def _build_user_response(doc: dict) -> UserResponse:
    uid = str(doc.get("_id", doc.get("id", "")))
    return UserResponse(
        id=uid,
        name=doc["name"],
        email=doc["email"],
        role=doc["role"],
        department=doc.get("department"),
        phone=doc.get("phone"),
        language=doc.get("language", "en"),
        created_at=doc.get("created_at", datetime.now(timezone.utc)).isoformat()
        if isinstance(doc.get("created_at"), datetime)
        else str(doc.get("created_at", "")),
    )


async def _send_reset_email(email: str, reset_token: str):
    """Send password reset email (uses project SMTP settings)."""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from config.settings import settings

        reset_url = f"http://localhost:3000/forgot-password?token={reset_token}"
        body = f"""
Hello,

You requested a password reset for your RTI-Agent account.

Click the link below to reset your password (valid for 30 minutes):
{reset_url}

If you did not request this, please ignore this email.

— RTI-Agent Team
        """
        msg = MIMEText(body)
        msg["Subject"] = "RTI-Agent — Password Reset Request"
        msg["From"] = settings.EMAIL_USER
        msg["To"] = email

        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
            server.sendmail(settings.EMAIL_USER, [email], msg.as_string())
        logger.info(f"[Auth] Reset email sent to {email}")
    except Exception as e:
        logger.warning(f"[Auth] Failed to send reset email: {e}")


# ── Routes ────────────────────────────────────────────────────────

@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new citizen or officer account",
)
async def register(payload: RegisterRequest):
    mongo = await get_mongo_client()

    # Check for existing user
    existing = await mongo.get_user_by_email(payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "EMAIL_EXISTS", "message": "An account with this email already exists."},
        )

    now = datetime.now(timezone.utc)
    user_doc = {
        "name": payload.name,
        "email": payload.email.lower(),
        "hashed_password": hash_password(payload.password),
        "role": payload.role,
        "department": payload.department,
        "phone": payload.phone,
        "language": payload.language,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }

    user_id = await mongo.create_user(user_doc)
    logger.info(f"[Auth] New {payload.role} registered: {payload.email}")

    access_token = create_access_token(user_id, payload.email, payload.role, payload.name)
    refresh_token = create_refresh_token(user_id)

    # Persist refresh token JTI for revocation support
    from jose import jwt as _jwt
    from config.settings import settings
    refresh_payload = _jwt.decode(
        refresh_token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        options={"verify_exp": False},
    )
    await mongo.save_refresh_token(
        jti=refresh_payload["jti"],
        user_id=user_id,
        expires_at=datetime.fromtimestamp(refresh_payload["exp"], tz=timezone.utc),
    )

    user_doc["_id"] = user_id
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=_build_user_response(user_doc),
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login with email and password",
)
async def login(payload: LoginRequest):
    mongo = await get_mongo_client()
    user = await mongo.get_user_by_email(payload.email)

    if not user or not verify_password(payload.password, user.get("hashed_password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "Invalid email or password."},
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "ACCOUNT_DISABLED", "message": "Your account has been disabled. Please contact support."},
        )

    user_id = str(user["_id"])
    access_token = create_access_token(user_id, user["email"], user["role"], user["name"])
    refresh_token = create_refresh_token(user_id)

    # Persist refresh token JTI
    from jose import jwt as _jwt
    from config.settings import settings
    refresh_payload = _jwt.decode(
        refresh_token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        options={"verify_exp": False},
    )
    await mongo.save_refresh_token(
        jti=refresh_payload["jti"],
        user_id=user_id,
        expires_at=datetime.fromtimestamp(refresh_payload["exp"], tz=timezone.utc),
    )

    logger.info(f"[Auth] User logged in: {user['email']} (role={user['role']})")
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=_build_user_response(user),
    )


@router.post(
    "/refresh",
    summary="Obtain a new access token using a refresh token",
)
async def refresh_token_endpoint(payload: RefreshRequest):
    mongo = await get_mongo_client()

    try:
        token_data = decode_token(payload.refresh_token, expected_type="refresh")
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_REFRESH_TOKEN", "message": "Refresh token is invalid or expired."},
        )

    jti = token_data.get("jti")
    if jti and await mongo.is_refresh_token_revoked(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "TOKEN_REVOKED", "message": "Refresh token has been revoked."},
        )

    user_id = token_data["sub"]
    user = await mongo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "USER_NOT_FOUND", "message": "User account not found."},
        )

    new_access_token = create_access_token(
        user_id, user["email"], user["role"], user["name"]
    )
    new_refresh_token = create_refresh_token(user_id)

    # Rotate: revoke old, persist new
    if jti:
        await mongo.revoke_refresh_token(jti)
    from jose import jwt as _jwt
    from config.settings import settings
    new_payload = _jwt.decode(
        new_refresh_token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        options={"verify_exp": False},
    )
    await mongo.save_refresh_token(
        jti=new_payload["jti"],
        user_id=user_id,
        expires_at=datetime.fromtimestamp(new_payload["exp"], tz=timezone.utc),
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout", summary="Revoke refresh token and end session")
async def logout(
    payload: RefreshRequest,
    current_user: dict = Depends(get_current_user),
):
    mongo = await get_mongo_client()
    try:
        token_data = decode_token(payload.refresh_token, expected_type="refresh")
        jti = token_data.get("jti")
        if jti:
            await mongo.revoke_refresh_token(jti)
    except Exception:
        pass  # Already invalid/expired — still return success

    logger.info(f"[Auth] User logged out: {current_user.get('email')}")
    return {"status": "success", "message": "Logged out successfully."}


@router.get("/me", response_model=UserResponse, summary="Get current user profile")
async def get_me(current_user: dict = Depends(get_current_user)):
    mongo = await get_mongo_client()
    user = await mongo.get_user_by_id(current_user["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "User not found."},
        )
    return _build_user_response(user)


@router.post("/change-password", summary="Change current user's password")
async def change_password(
    payload: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
):
    mongo = await get_mongo_client()
    user = await mongo.get_user_by_id(current_user["sub"])
    if not user:
        raise HTTPException(status_code=404, detail={"code": "USER_NOT_FOUND", "message": "User not found."})

    if not verify_password(payload.current_password, user.get("hashed_password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "WRONG_PASSWORD", "message": "Current password is incorrect."},
        )

    await mongo.update_user(str(user["_id"]), {"hashed_password": hash_password(payload.new_password)})
    logger.info(f"[Auth] Password changed for: {user['email']}")
    return {"status": "success", "message": "Password updated successfully."}


@router.post("/forgot-password", summary="Request a password reset email")
async def forgot_password(payload: ForgotPasswordRequest):
    mongo = await get_mongo_client()
    user = await mongo.get_user_by_email(payload.email)

    # Always return success (don't leak whether email exists)
    if user:
        reset_token = create_reset_token(str(user["_id"]), user["email"])
        await _send_reset_email(user["email"], reset_token)

    return {
        "status": "success",
        "message": "If an account exists with that email, a reset link has been sent.",
    }


@router.post("/reset-password", summary="Reset password using a valid reset token")
async def reset_password(payload: ResetPasswordRequest):
    mongo = await get_mongo_client()
    try:
        token_data = decode_token(payload.token, expected_type="reset")
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_RESET_TOKEN", "message": "Reset token is invalid or has expired."},
        )

    user = await mongo.get_user_by_id(token_data["sub"])
    if not user:
        raise HTTPException(status_code=404, detail={"code": "USER_NOT_FOUND", "message": "User not found."})

    await mongo.update_user(str(user["_id"]), {"hashed_password": hash_password(payload.new_password)})
    logger.info(f"[Auth] Password reset for: {user['email']}")
    return {"status": "success", "message": "Password reset successfully. Please log in."}


# ── Admin Seed ────────────────────────────────────────────────────

async def seed_admin_user():
    """
    Ensure the admin account exists at startup.
    Uses ADMIN_SEED_EMAIL / ADMIN_SEED_PASSWORD / ADMIN_SEED_NAME from settings.
    Safe to call multiple times — skips if admin already exists.
    """
    from config.settings import settings
    try:
        mongo = await get_mongo_client()
        existing = await mongo.get_user_by_email(settings.ADMIN_SEED_EMAIL)
        if existing:
            logger.info(f"[Auth] Admin already exists: {settings.ADMIN_SEED_EMAIL}")
            return

        now = datetime.now(timezone.utc)
        await mongo.create_user({
            "name": settings.ADMIN_SEED_NAME,
            "email": settings.ADMIN_SEED_EMAIL.lower(),
            "hashed_password": hash_password(settings.ADMIN_SEED_PASSWORD),
            "role": "admin",
            "department": None,
            "phone": None,
            "language": "en",
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        })
        logger.info(f"[Auth] Admin user seeded: {settings.ADMIN_SEED_EMAIL}")
    except Exception as e:
        logger.error(f"[Auth] Admin seed failed: {e}")
