from decimal import Decimal, ROUND_HALF_UP
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import text

from backend.db.connection import engine
from backend.schemas.order import OrderCreateRequest


def create_order_from_cart(payload: OrderCreateRequest) -> dict[str, Any]:
    cart_query = text("""
        SELECT
            cart_id,
            user_id,
            cart_status
        FROM carts
        WHERE cart_id = :cart_id
          AND cart_status = 'active'
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
            (ci.quantity * ci.unit_price) AS line_total
        FROM cart_items ci
        JOIN products p
          ON p.product_id = ci.product_id
        WHERE ci.cart_id = :cart_id
        ORDER BY ci.added_at ASC
    """)

    coupon_query = text("""
        SELECT
            coupon_id,
            coupon_name,
            coupon_type,
            discount_value,
            minimum_order_amount,
            coupon_status,
            valid_start_at,
            valid_end_at
        FROM coupons
        WHERE coupon_name = :coupon_name
          AND coupon_status = 'active'
          AND valid_start_at <= CURRENT_TIMESTAMP
          AND valid_end_at >= CURRENT_TIMESTAMP
        LIMIT 1
    """)

    insert_order_query = text("""
        INSERT INTO orders (
            user_id,
            cart_id,
            coupon_id,
            order_status,
            subtotal_amount,
            discount_amount,
            total_amount,
            currency,
            ordered_at,
            created_at,
            updated_at
        )
        VALUES (
            :user_id,
            :cart_id,
            :coupon_id,
            'created',
            :subtotal_amount,
            :discount_amount,
            :total_amount,
            :currency,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        )
        RETURNING
            order_id,
            user_id,
            cart_id,
            order_status,
            subtotal_amount,
            discount_amount,
            total_amount,
            currency,
            ordered_at
    """)

    insert_order_item_query = text("""
        INSERT INTO order_items (
            order_id,
            product_id,
            quantity,
            unit_price,
            discount_amount,
            final_item_amount,
            currency,
            line_total,
            created_at,
            updated_at
        )
        VALUES (
            :order_id,
            :product_id,
            :quantity,
            :unit_price,
            :discount_amount,
            :final_item_amount,
            :currency,
            :line_total,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        )
        RETURNING
            order_item_id,
            product_id,
            quantity,
            unit_price,
            final_item_amount,
            line_total,
            currency
    """)

    update_cart_query = text("""
        UPDATE carts
        SET
            cart_status = 'checked_out',
            checked_out_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE cart_id = :cart_id
    """)

    with engine.begin() as connection:
        cart = connection.execute(
            cart_query,
            {"cart_id": payload.cart_id},
        ).mappings().first()

        if cart is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active cart not found",
            )

        item_rows = connection.execute(
            cart_items_query,
            {"cart_id": payload.cart_id},
        ).mappings().all()

        if not item_rows:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is empty",
            )

        subtotal_amount = Decimal("0")
        currency: str | None = None
        prepared_items: list[dict[str, Any]] = []

        for row in item_rows:
            line_total = Decimal(str(row["line_total"]))
            subtotal_amount += line_total
            if currency is None:
                currency = row["currency"]

            prepared_items.append(
                {
                    "product_id": row["product_id"],
                    "product_name": row["product_name"],
                    "quantity": row["quantity"],
                    "unit_price": Decimal(str(row["unit_price"])),
                    "discount_amount": Decimal("0"),
                    "final_item_amount": line_total,
                    "line_total": line_total,
                    "currency": row["currency"],
                }
            )

        discount_amount = Decimal("0")
        coupon_id: UUID | None = None
        coupon_name: str | None = None

        if payload.coupon_name is not None:
            coupon = connection.execute(
                coupon_query,
                {"coupon_name": payload.coupon_name},
            ).mappings().first()

            if coupon is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Coupon not found",
                )

            minimum_order_amount = Decimal(str(coupon["minimum_order_amount"]))
            discount_value = Decimal(str(coupon["discount_value"]))

            if subtotal_amount < minimum_order_amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cart total does not meet coupon minimum order amount",
                )

            if coupon["coupon_type"] == "percentage":
                discount_amount = (
                    subtotal_amount * discount_value / Decimal("100")
                ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            elif coupon["coupon_type"] == "fixed_amount":
                discount_amount = discount_value
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unsupported coupon type",
                )

            if discount_amount > subtotal_amount:
                discount_amount = subtotal_amount

            coupon_id = coupon["coupon_id"]
            coupon_name = coupon["coupon_name"]

        total_amount = subtotal_amount - discount_amount

        created_order = connection.execute(
            insert_order_query,
            {
                "user_id": cart["user_id"],
                "cart_id": payload.cart_id,
                "coupon_id": coupon_id,
                "subtotal_amount": subtotal_amount,
                "discount_amount": discount_amount,
                "total_amount": total_amount,
                "currency": currency,
            },
        ).mappings().first()

        if created_order is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create order",
            )

        created_items: list[dict[str, Any]] = []

        for item in prepared_items:
            created_order_item = connection.execute(
                insert_order_item_query,
                {
                    "order_id": created_order["order_id"],
                    "product_id": item["product_id"],
                    "quantity": item["quantity"],
                    "unit_price": item["unit_price"],
                    "discount_amount": item["discount_amount"],
                    "final_item_amount": item["final_item_amount"],
                    "line_total": item["line_total"],
                    "currency": item["currency"],
                },
            ).mappings().first()

            if created_order_item is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create order item",
                )

            created_items.append(
                {
                    "order_item_id": created_order_item["order_item_id"],
                    "product_id": created_order_item["product_id"],
                    "product_name": item["product_name"],
                    "quantity": created_order_item["quantity"],
                    "unit_price": created_order_item["unit_price"],
                    "line_total": created_order_item["line_total"],
                    "currency": created_order_item["currency"],
                }
            )

        connection.execute(
            update_cart_query,
            {"cart_id": payload.cart_id},
        )

    return {
        "order_id": created_order["order_id"],
        "user_id": created_order["user_id"],
        "cart_id": created_order["cart_id"],
        "order_status": created_order["order_status"],
        "subtotal_amount": created_order["subtotal_amount"],
        "discount_amount": created_order["discount_amount"],
        "total_amount": created_order["total_amount"],
        "currency": created_order["currency"],
        "coupon_name": coupon_name,
        "ordered_at": created_order["ordered_at"],
        "items": created_items,
        "message": "Order created successfully",
    }