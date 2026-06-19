"""
api/auth/password.py
--------------------
Secure password hashing using bcrypt directly.

Uses the `bcrypt` library directly (not passlib) to avoid passlib's
version-detection issues with bcrypt >= 4.x.
"""

import bcrypt


def hash_password(plain: str) -> str:
    """Hash a plain-text password using bcrypt (12 rounds)."""
    # bcrypt has a 72-byte input limit — encode and truncate safely
    password_bytes = plain.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain-text password against its bcrypt hash."""
    try:
        password_bytes = plain.encode("utf-8")
        hashed_bytes = hashed.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False
