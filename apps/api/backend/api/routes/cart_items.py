from uuid import UUID

from fastapi import APIRouter, status

from backend.schemas.cart_item import CartItemCreateRequest, CartItemResponse
from backend.services.cart_item_service import add_item_to_cart

router = APIRouter(prefix="/carts", tags=["carts"])


@router.post(
    "/{cart_id}/items",
    response_model=CartItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_cart_item(cart_id: UUID, payload: CartItemCreateRequest) -> CartItemResponse:
    item = add_item_to_cart(cart_id, payload)
    return CartItemResponse(**item)