from decimal import Decimal
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import text

from backend.db.connection import engine


def prepare_checkout(cart_id: UUID) -> dict[str, Any]:
    cart_query = text("""
        SELECT
            c.cart_id,
            c.user_id,
            c.cart_status,
            c.created_at,
            c.updated_at,
            c.checked_out_at,
            u.email,
            u.user_name,
            u.user_status,
            u.marketing_opt_in_yn
        FROM carts c
        JOIN users u
          ON u.user_id = c.user_id
        WHERE c.cart_id = :cart_id
          AND c.cart_status = 'active'
        LIMIT 1
    """)

    cart_items_query = text("""
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

    available_coupons_query = text("""
        SELECT
            coupon_id,
            campaign_id,
            coupon_name,
            coupon_type,
            discount_value,
            minimum_order_amount,
            coupon_status,
            valid_start_at,
            valid_end_at
        FROM coupons
        WHERE coupon_status = 'active'
          AND valid_start_at <= CURRENT_TIMESTAMP
          AND valid_end_at >= CURRENT_TIMESTAMP
        ORDER BY minimum_order_amount ASC, coupon_name ASC
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
            cart_items_query,
            {"cart_id": cart_id},
        ).mappings().all()

        if not item_rows:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is empty",
            )

        coupon_rows = connection.execute(available_coupons_query).mappings().all()

    items: list[dict[str, Any]] = []
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

    available_coupons = []
    for row in coupon_rows:
        if total_amount >= row["minimum_order_amount"]:
            available_coupons.append(
                {
                    "coupon_id": row["coupon_id"],
                    "campaign_id": row["campaign_id"],
                    "coupon_name": row["coupon_name"],
                    "coupon_type": row["coupon_type"],
                    "discount_value": row["discount_value"],
                    "minimum_order_amount": row["minimum_order_amount"],
                    "coupon_status": row["coupon_status"],
                    "valid_start_at": row["valid_start_at"],
                    "valid_end_at": row["valid_end_at"],
                }
            )

    return {
        "cart_id": cart["cart_id"],
        "user_id": cart["user_id"],
        "cart_status": cart["cart_status"],
        "total_items": total_items,
        "total_quantity": total_quantity,
        "total_amount": total_amount,
        "currency": currency,
        "items": items,
        "user": {
            "user_id": cart["user_id"],
            "email": cart["email"],
            "user_name": cart["user_name"],
            "user_status": cart["user_status"],
            "marketing_opt_in_yn": cart["marketing_opt_in_yn"],
        },
        "available_coupons": available_coupons,
    }