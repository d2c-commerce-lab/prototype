from decimal import Decimal
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import text

from backend.db.connection import engine


def get_order_history(user_id: UUID) -> dict[str, Any]:
    user_query = text("""
        SELECT
            user_id
        FROM users
        WHERE user_id = :user_id
        LIMIT 1
    """)

    orders_query = text("""
        SELECT
            o.order_id,
            o.user_id,
            o.cart_id,
            o.order_status,
            o.subtotal_amount,
            o.discount_amount,
            o.total_amount,
            o.currency,
            c.coupon_name,
            o.ordered_at,
            (
                SELECT p.payment_status
                FROM payments p
                WHERE p.order_id = o.order_id
                ORDER BY p.created_at DESC
                LIMIT 1
            ) AS payment_status
        FROM orders o
        LEFT JOIN coupons c
          ON c.coupon_id = o.coupon_id
        WHERE o.user_id = :user_id
        ORDER BY o.ordered_at DESC, o.created_at DESC
    """)

    order_items_query = text("""
        SELECT
            oi.order_item_id,
            oi.order_id,
            oi.product_id,
            p.product_name,
            oi.quantity,
            oi.unit_price,
            oi.line_total,
            oi.currency
        FROM order_items oi
        JOIN products p
          ON p.product_id = oi.product_id
        WHERE oi.order_id = :order_id
        ORDER BY oi.created_at ASC
    """)

    with engine.connect() as connection:
        user = connection.execute(
            user_query,
            {"user_id": user_id},
        ).mappings().first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        order_rows = connection.execute(
            orders_query,
            {"user_id": user_id},
        ).mappings().all()

        orders: list[dict[str, Any]] = []

        for order_row in order_rows:
            item_rows = connection.execute(
                order_items_query,
                {"order_id": order_row["order_id"]},
            ).mappings().all()

            items = [
                {
                    "order_item_id": item["order_item_id"],
                    "product_id": item["product_id"],
                    "product_name": item["product_name"],
                    "quantity": item["quantity"],
                    "unit_price": Decimal(str(item["unit_price"])),
                    "line_total": Decimal(str(item["line_total"])),
                    "currency": item["currency"],
                }
                for item in item_rows
            ]

            orders.append(
                {
                    "order_id": order_row["order_id"],
                    "cart_id": order_row["cart_id"],
                    "order_status": order_row["order_status"],
                    "payment_status": order_row["payment_status"],
                    "subtotal_amount": Decimal(str(order_row["subtotal_amount"])),
                    "discount_amount": Decimal(str(order_row["discount_amount"])),
                    "total_amount": Decimal(str(order_row["total_amount"])),
                    "currency": order_row["currency"],
                    "coupon_name": order_row["coupon_name"],
                    "ordered_at": order_row["ordered_at"],
                    "items": items,
                }
            )

    return {
        "user_id": user_id,
        "total_orders": len(orders),
        "orders": orders,
    }