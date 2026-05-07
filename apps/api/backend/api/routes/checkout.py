from uuid import UUID

from fastapi import APIRouter, status

from backend.schemas.checkout import CheckoutResponse
from backend.services.checkout_service import prepare_checkout

router = APIRouter(prefix="/carts", tags=["checkout"])


@router.post(
    "/{cart_id}/checkout",
    response_model=CheckoutResponse,
    status_code=status.HTTP_200_OK,
)
def enter_checkout(cart_id: UUID) -> CheckoutResponse:
    checkout_data = prepare_checkout(cart_id)
    return CheckoutResponse(**checkout_data)