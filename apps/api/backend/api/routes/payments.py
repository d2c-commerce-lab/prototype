from fastapi import APIRouter, status
from backend.schemas.payment import (
    PaymentSimulationRequest,
    PaymentSimulationResponse,
)
from backend.services.payment_service import simulate_payment

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post(
    "/simulate",
    response_model=PaymentSimulationResponse,
    status_code=status.HTTP_200_OK,
)
def simulate_order_payment(
    payload: PaymentSimulationRequest,
) -> PaymentSimulationResponse:
    result = simulate_payment(payload)
    return PaymentSimulationResponse(**result)