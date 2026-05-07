from decimal import Decimal
from typing import Any
from uuid import UUID

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


def get_cart_detail(cart_id: UUID) -> dict[str, Any]:
    cart_query = text("""
        SELECT
            cart_id,
            user_id,
            cart_status,
            created_at,
            updated_at,
            checked_out_at
        FROM carts
        WHERE cart_id = :cart_id
          AND cart_status = 'active'
        LIMIT 1
    """)

    items_query = text("""
        SELECT
            ci.cart_item_id,
            ci.product_id,
            p.product_name,
            ci.quantity,
            ci.unit_price,
            ci.currency,
            (ci.quantity * ci.unit_price) AS line_total,
            ci.added_at,
            ci.updated_at
        FROM cart_items ci
        JOIN products p
          ON p.product_id = ci.product_id
        WHERE ci.cart_id = :cart_id
        ORDER BY ci.added_at ASC
    """)

    with engine.connect() as connection:
        cart = connection.execute(
            cart_query,
            {"cart_id": cart_id},
        ).mappings().first()

        if cart is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active cart not found",
            )

        item_rows = connection.execute(
            items_query,
            {"cart_id": cart_id},
        ).mappings().all()

    items = []
    total_items = len(item_rows)
    total_quantity = 0
    total_amount = Decimal("0")
    currency: str | None = None

    for row in item_rows:
        line_total = row["line_total"]
        total_quantity += row["quantity"]
        total_amount += line_total
        if currency is None:
            currency = row["currency"]

        items.append(
            {
                "cart_item_id": row["cart_item_id"],
                "product_id": row["product_id"],
                "product_name": row["product_name"],
                "quantity": row["quantity"],
                "unit_price": row["unit_price"],
                "currency": row["currency"],
                "line_total": line_total,
                "added_at": row["added_at"],
                "updated_at": row["updated_at"],
            }
        )

    return {
        "cart_id": cart["cart_id"],
        "user_id": cart["user_id"],
        "cart_status": cart["cart_status"],
        "created_at": cart["created_at"],
        "updated_at": cart["updated_at"],
        "checked_out_at": cart["checked_out_at"],
        "total_items": total_items,
        "total_quantity": total_quantity,
        "total_amount": total_amount,
        "currency": currency,
        "items": items,
    }