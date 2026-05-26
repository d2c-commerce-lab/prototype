import logging
from decimal import Decimal, ROUND_HALF_UP
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import text

from backend.db.connection import engine
from backend.schemas.coupon_apply import CouponApplyRequest
from backend.services.event_log_service import record_event


logger = logging.getLogger(__name__)


def record_domain_event_safely(
    *,
    event_name: str,
    user_id: UUID | None,
    entity_type: str | None,
    entity_id: UUID | None,
    properties: dict[str, Any],
) -> None:
    try:
        record_event(
            event_name=event_name,
            event_type="domain_event",
            source="backend",
            user_id=user_id,
            session_id=None,
            entity_type=entity_type,
            entity_id=entity_id,
            properties=properties,
        )
    except Exception:  # pylint: disable=broad-exception-caught
        logger.exception("Failed to record domain event: %s", event_name)

def apply_coupon_to_cart(cart_id: UUID, payload: CouponApplyRequest) -> dict[str, Any]:
    cart_query = text("""
        SELECT
            c.cart_id,
            c.user_id,
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

    used_coupon_query = text("""
        SELECT
            order_id
        FROM orders
        WHERE user_id = :user_id
        AND coupon_id = :coupon_id
        AND order_status = 'paid'
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
        
        used_coupon = connection.execute(
            used_coupon_query,
            {
                "user_id": cart["user_id"],
                "coupon_id": coupon["coupon_id"],
            },
        ).mappings().first()

        if used_coupon is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Coupon has already been used",
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

    record_domain_event_safely(
        event_name="coupon_applied",
        user_id=cart["user_id"],
        entity_type="coupon",
        entity_id=coupon["coupon_id"],
        properties={
            "cart_id": cart_id,
            "coupon_id": coupon["coupon_id"],
            "coupon_name": coupon["coupon_name"],
            "coupon_type": coupon["coupon_type"],
            "discount_value": discount_value,
            "minimum_order_amount": minimum_order_amount,
            "total_amount": total_amount,
            "discount_amount": discount_amount,
            "final_amount": final_amount,
            "currency": currency,
        },
    )

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

def list_user_coupons(user_id: UUID) -> dict[str, Any]:
    user_query = text("""
        SELECT
            user_id
        FROM users
        WHERE user_id = :user_id
          AND user_status = 'active'
        LIMIT 1
    """)

    available_coupons_query = text("""
        SELECT
            c.coupon_id,
            c.campaign_id,
            c.coupon_name,
            c.coupon_type,
            c.discount_value,
            c.minimum_order_amount,
            c.coupon_status,
            c.valid_start_at,
            c.valid_end_at
        FROM coupons c
        WHERE c.coupon_status = 'active'
          AND c.valid_start_at <= CURRENT_TIMESTAMP
          AND c.valid_end_at >= CURRENT_TIMESTAMP
          AND NOT EXISTS (
              SELECT 1
              FROM orders o
              WHERE o.user_id = :user_id
                AND o.coupon_id = c.coupon_id
                AND o.order_status = 'paid'
          )
        ORDER BY c.valid_end_at ASC, c.coupon_name ASC
    """)

    used_coupons_query = text("""
        SELECT
            c.coupon_id,
            c.campaign_id,
            c.coupon_name,
            c.coupon_type,
            c.discount_value,
            c.minimum_order_amount,
            c.coupon_status,
            c.valid_start_at,
            c.valid_end_at,
            o.order_id AS used_order_id,
            COALESCE(p.paid_at, p.created_at, o.ordered_at) AS used_at,
            p.payment_id
        FROM orders o
        JOIN coupons c
          ON c.coupon_id = o.coupon_id
        LEFT JOIN LATERAL (
            SELECT
                payment_id,
                paid_at,
                created_at
            FROM payments
            WHERE order_id = o.order_id
              AND payment_status = 'paid'
            ORDER BY COALESCE(paid_at, created_at) DESC
            LIMIT 1
        ) p ON TRUE
        WHERE o.user_id = :user_id
          AND o.order_status = 'paid'
          AND o.coupon_id IS NOT NULL
        ORDER BY COALESCE(p.paid_at, p.created_at, o.ordered_at) DESC
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

        available_coupons = connection.execute(
            available_coupons_query,
            {"user_id": user_id},
        ).mappings().all()

        used_coupons = connection.execute(
            used_coupons_query,
            {"user_id": user_id},
        ).mappings().all()

    return {
        "user_id": user_id,
        "available_coupons": [dict(coupon) for coupon in available_coupons],
        "used_coupons": [dict(coupon) for coupon in used_coupons],
    }