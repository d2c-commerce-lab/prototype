from fastapi import APIRouter, status

from backend.schemas.order import OrderCreateRequest, OrderCreateResponse
from backend.services.order_service import create_order_from_cart

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderCreateResponse, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreateRequest) -> OrderCreateResponse:
    order = create_order_from_cart(payload)
    return OrderCreateResponse(**order)