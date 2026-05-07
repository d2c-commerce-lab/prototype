from datetime import datetime
from decimal import Decimal
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import text

from backend.db.connection import engine
from backend.schemas.payment import PaymentSimulationRequest


def simulate_payment(payload: PaymentSimulationRequest) -> dict[str, Any]:
    order_query = text("""
        SELECT
            order_id,
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
            CURRENT_TIMESTAMP,
            :paid_at,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
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
            updated_at = CURRENT_TIMESTAMP
        WHERE order_id = :order_id
    """)

    update_order_failed_query = text("""
        UPDATE orders
        SET
            order_status = 'payment_failed',
            updated_at = CURRENT_TIMESTAMP
        WHERE order_id = :order_id
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

        if payload.simulate_result == "success":
            payment_status = "paid"
            paid_amount = requested_amount
            approved_amount = requested_amount
            failure_code = None
            paid_at = datetime.now()
            pg_provider = "mock_pg"
            transaction_id = f"tx-{payload.order_id}"
            connection.execute(
                update_order_success_query,
                {"order_id": payload.order_id},
            )
        else:
            payment_status = "failed"
            paid_amount = Decimal("0")
            approved_amount = Decimal("0")
            failure_code = "SIMULATED_FAILURE"
            paid_at = None
            pg_provider = "mock_pg"
            transaction_id = None
            connection.execute(
                update_order_failed_query,
                {"order_id": payload.order_id},
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
            },
        ).mappings().first()

        if created_payment is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create payment",
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