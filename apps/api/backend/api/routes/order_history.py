from uuid import UUID

from fastapi import APIRouter, status

from backend.schemas.order_history import OrderHistoryListResponse
from backend.services.order_history_service import get_order_history

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=OrderHistoryListResponse, status_code=status.HTTP_200_OK)
def get_orders(user_id: UUID) -> OrderHistoryListResponse:
    result = get_order_history(user_id)
    return OrderHistoryListResponse(**result)