from decimal import Decimal, ROUND_HALF_UP
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import text

from backend.db.connection import engine
from backend.schemas.coupon_apply import CouponApplyRequest


def apply_coupon_to_cart(cart_id: UUID, payload: CouponApplyRequest) -> dict[str, Any]:
    cart_query = text("""
        SELECT
            c.cart_id,
            c.cart_status
        FROM carts c
        WHERE c.cart_id = :cart_id
          AND c.cart_status = 'active'
        LIMIT 1
    """)

    cart_items_total_query = text("""
        SELECT
            COALESCE(SUM(ci.quantity * ci.unit_price), 0) AS total_amount,
            MAX(ci.currency) AS currency
        FROM cart_items ci
        WHERE ci.cart_id = :cart_id
    """)

    coupon_query = text("""
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
        WHERE coupon_name = :coupon_name
          AND coupon_status = 'active'
          AND valid_start_at <= CURRENT_TIMESTAMP
          AND valid_end_at >= CURRENT_TIMESTAMP
        LIMIT 1
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

        total_row = connection.execute(
            cart_items_total_query,
            {"cart_id": cart_id},
        ).mappings().first()

        if total_row is None or Decimal(str(total_row["total_amount"])) <= Decimal("0"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is empty",
            )

        coupon = connection.execute(
            coupon_query,
            {"coupon_name": payload.coupon_name},
        ).mappings().first()

        if coupon is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Coupon not found",
            )

    total_amount = Decimal(str(total_row["total_amount"]))
    currency = total_row["currency"]

    minimum_order_amount = Decimal(str(coupon["minimum_order_amount"]))
    discount_value = Decimal(str(coupon["discount_value"]))

    if total_amount < minimum_order_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart total does not meet coupon minimum order amount",
        )

    if coupon["coupon_type"] == "percentage":
        discount_amount = (total_amount * discount_value / Decimal("100")).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
    elif coupon["coupon_type"] == "fixed_amount":
        discount_amount = discount_value
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported coupon type",
        )

    if discount_amount > total_amount:
        discount_amount = total_amount

    final_amount = total_amount - discount_amount

    return {
        "cart_id": cart_id,
        "coupon": {
            "coupon_id": coupon["coupon_id"],
            "campaign_id": coupon["campaign_id"],
            "coupon_name": coupon["coupon_name"],
            "coupon_type": coupon["coupon_type"],
            "discount_value": discount_value,
            "minimum_order_amount": minimum_order_amount,
            "coupon_status": coupon["coupon_status"],
            "valid_start_at": coupon["valid_start_at"],
            "valid_end_at": coupon["valid_end_at"],
        },
        "total_amount": total_amount,
        "discount_amount": discount_amount,
        "final_amount": final_amount,
        "currency": currency,
        "message": "Coupon applied successfully",
    }