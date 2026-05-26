import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import text

from backend.db.connection import engine
from backend.schemas.payment import PaymentSimulationRequest
from backend.services.event_log_service import record_event


KST = timezone(timedelta(hours=9))

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

def now_kst_naive() -> datetime:
    return datetime.now(KST).replace(tzinfo=None)

def simulate_payment(payload: PaymentSimulationRequest) -> dict[str, Any]:
    order_query = text("""
        SELECT
            order_id,
            user_id,
            cart_id,
            coupon_id,
            order_status,
            total_amount,
            currency
        FROM orders
        WHERE order_id = :order_id
        LIMIT 1
    """)

    insert_payment_query = text("""
        INSERT INTO payments (
            order_id,
            payment_method,
            payment_status,
            paid_amount,
            currency,
            pg_provider,
            transaction_id,
            failure_code,
            requested_at,
            paid_at,
            created_at,
            updated_at
        )
        VALUES (
            :order_id,
            :payment_method,
            :payment_status,
            :paid_amount,
            :currency,
            :pg_provider,
            :transaction_id,
            :failure_code,
            :now,
            :paid_at,
            :now,
            :now
        )
        RETURNING
            payment_id,
            order_id,
            payment_method,
            payment_status,
            paid_amount,
            currency,
            pg_provider,
            transaction_id,
            failure_code,
            requested_at,
            paid_at,
            created_at
    """)

    update_order_success_query = text("""
        UPDATE orders
        SET
            order_status = 'paid',
            updated_at = :now
        WHERE order_id = :order_id
    """)

    update_order_failed_query = text("""
        UPDATE orders
        SET
            order_status = 'payment_failed',
            updated_at = :now
        WHERE order_id = :order_id
    """)

    update_cart_checked_out_query = text("""
        UPDATE carts
        SET
            cart_status = 'checked_out',
            checked_out_at = :now,
            updated_at = :now
        WHERE cart_id = :cart_id
        AND cart_status = 'active'
    """)

    with engine.begin() as connection:
        order = connection.execute(
            order_query,
            {"order_id": payload.order_id},
        ).mappings().first()

        if order is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )

        if order["order_status"] not in ("created", "payment_failed"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order is not payable",
            )

        requested_amount = Decimal(str(order["total_amount"]))
        currency = order["currency"]
        now = now_kst_naive()

        if payload.simulate_result == "success":
            payment_status = "paid"
            paid_amount = requested_amount
            failure_code = None
            paid_at = now
            pg_provider = "mock_pg"
            transaction_id = f"tx-{payload.order_id}"

            connection.execute(
                update_order_success_query,
                {
                    "order_id": payload.order_id,
                    "now": now,
                },
            )

            connection.execute(
                update_cart_checked_out_query,
                {
                    "cart_id": order["cart_id"],
                    "now": now,
                },
            )
        else:
            payment_status = "failed"
            paid_amount = Decimal("0")
            failure_code = "SIMULATED_FAILURE"
            paid_at = None
            pg_provider = "mock_pg"
            transaction_id = None
            
            connection.execute(
                update_order_failed_query,
                {
                    "order_id": payload.order_id,
                    "now": now,
                },
            )

        created_payment = connection.execute(
            insert_payment_query,
            {
                "order_id": payload.order_id,
                "payment_method": payload.payment_method,
                "payment_status": payment_status,
                "paid_amount": paid_amount,
                "currency": currency,
                "pg_provider": pg_provider,
                "transaction_id": transaction_id,
                "failure_code": failure_code,
                "paid_at": paid_at,
                "now": now,
            },
        ).mappings().first()

        if created_payment is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create payment",
            )

    if created_payment["payment_status"] == "paid":
        record_domain_event_safely(
            event_name="payment_succeeded",
            user_id=order["user_id"],
            entity_type="payment",
            entity_id=created_payment["payment_id"],
            properties={
                "payment_id": created_payment["payment_id"],
                "order_id": created_payment["order_id"],
                "cart_id": order["cart_id"],
                "payment_method": created_payment["payment_method"],
                "payment_status": created_payment["payment_status"],
                "requested_amount": requested_amount,
                "approved_amount": created_payment["paid_amount"],
                "currency": created_payment["currency"],
                "pg_provider": created_payment["pg_provider"],
                "transaction_id": created_payment["transaction_id"],
            },
        )

        record_domain_event_safely(
            event_name="cart_checked_out",
            user_id=order["user_id"],
            entity_type="cart",
            entity_id=order["cart_id"],
            properties={
                "cart_id": order["cart_id"],
                "order_id": created_payment["order_id"],
                "payment_id": created_payment["payment_id"],
                "cart_status": "checked_out",
            },
        )

        if order["coupon_id"] is not None:
            record_domain_event_safely(
                event_name="coupon_used",
                user_id=order["user_id"],
                entity_type="coupon",
                entity_id=order["coupon_id"],
                properties={
                    "coupon_id": order["coupon_id"],
                    "order_id": created_payment["order_id"],
                    "payment_id": created_payment["payment_id"],
                    "cart_id": order["cart_id"],
                },
            )
    else:
        record_domain_event_safely(
            event_name="payment_failed",
            user_id=order["user_id"],
            entity_type="payment",
            entity_id=created_payment["payment_id"],
            properties={
                "payment_id": created_payment["payment_id"],
                "order_id": created_payment["order_id"],
                "cart_id": order["cart_id"],
                "payment_method": created_payment["payment_method"],
                "payment_status": created_payment["payment_status"],
                "requested_amount": requested_amount,
                "approved_amount": created_payment["paid_amount"],
                "currency": created_payment["currency"],
                "failure_code": created_payment["failure_code"],
            },
        )

    return {
        "payment_id": created_payment["payment_id"],
        "order_id": created_payment["order_id"],
        "payment_method": created_payment["payment_method"],
        "payment_status": created_payment["payment_status"],
        "requested_amount": requested_amount,
        "approved_amount": created_payment["paid_amount"],
        "failed_reason": created_payment["failure_code"],
        "paid_at": created_payment["paid_at"],
        "created_at": created_payment["created_at"],
        "message": "Payment simulated successfully",
    }