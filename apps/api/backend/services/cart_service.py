from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import text

from backend.db.connection import engine
from backend.schemas.cart import CartCreateRequest


def create_or_get_active_cart(payload: CartCreateRequest) -> dict[str, Any]:
    select_query = text("""
        SELECT
            cart_id,
            user_id,
            cart_status,
            created_at,
            updated_at,
            checked_out_at
        FROM carts
        WHERE user_id = :user_id
          AND cart_status = 'active'
        ORDER BY created_at DESC
        LIMIT 1
    """)

    insert_query = text("""
        INSERT INTO carts (
            user_id,
            cart_status,
            created_at,
            updated_at,
            checked_out_at
        )
        VALUES (
            :user_id,
            'active',
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP,
            NULL
        )
        RETURNING
            cart_id,
            user_id,
            cart_status,
            created_at,
            updated_at,
            checked_out_at
    """)

    with engine.begin() as connection:
        existing = connection.execute(
            select_query,
            {"user_id": payload.user_id},
        ).mappings().first()
        if existing is not None:
            return {
                "cart_id": existing["cart_id"],
                "user_id": existing["user_id"],
                "cart_status": existing["cart_status"],
                "created_at": existing["created_at"],
                "updated_at": existing["updated_at"],
                "checked_out_at": existing["checked_out_at"],
            }

        created = connection.execute(
            insert_query,
            {"user_id": payload.user_id},
        ).mappings().first()

        if created is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create cart",
            )

        return {
            "cart_id": created["cart_id"],
            "user_id": created["user_id"],
            "cart_status": created["cart_status"],
            "created_at": created["created_at"],
            "updated_at": created["updated_at"],
            "checked_out_at": created["checked_out_at"],
        }