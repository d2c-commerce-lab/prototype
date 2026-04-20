from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import text

from backend.db.connection import engine
from backend.schemas.auth import LoginRequest, SignupRequest

try:
    import bcrypt
except ImportError as exc:  # pragma: no cover
    raise RuntimeError(
        "bcrypt is required. Install it with: pip install bcrypt"
    ) from exc


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    password_bytes = password.encode("utf-8")
    password_hash_bytes = password_hash.encode("utf-8")
    return bcrypt.checkpw(password_bytes, password_hash_bytes)


def create_user(payload: SignupRequest) -> dict[str, Any]:
    check_query = text("""
        SELECT user_id
        FROM users
        WHERE email = :email
        LIMIT 1
    """)

    insert_query = text("""
        INSERT INTO users (
            email,
            user_name,
            password_hash,
            signup_at,
            user_status,
            marketing_opt_in_yn,
            created_at,
            updated_at
        )
        VALUES (
            :email,
            :user_name,
            :password_hash,
            CURRENT_TIMESTAMP,
            'active',
            :marketing_opt_in_yn,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        )
        RETURNING
            user_id,
            email,
            user_name,
            user_status,
            marketing_opt_in_yn
    """)

    with engine.begin() as connection:
        existing = connection.execute(
            check_query,
            {"email": payload.email},
        ).mappings().first()

        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists",
            )

        result = connection.execute(
            insert_query,
            {
                "email": payload.email,
                "user_name": payload.user_name,
                "password_hash": hash_password(payload.password),
                "marketing_opt_in_yn": payload.marketing_opt_in_yn,
            },
        ).mappings().first()

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user",
        )

    return dict(result)


def authenticate_user(payload: LoginRequest) -> dict[str, Any]:
    query = text("""
        SELECT
            user_id,
            email,
            user_name,
            password_hash,
            user_status
        FROM users
        WHERE email = :email
        LIMIT 1
    """)

    with engine.connect() as connection:
        user = connection.execute(
            query,
            {"email": payload.email},
        ).mappings().first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    if not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    return {
        "user_id": user["user_id"],
        "email": user["email"],
        "user_name": user["user_name"],
        "user_status": user["user_status"],
        "message": "Login successful",
    }