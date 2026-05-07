from uuid import UUID

from fastapi import APIRouter, status

from backend.schemas.cart_item import (
    CartItemCreateRequest,
    CartItemDeleteResponse,
    CartItemResponse,
)
from backend.services.cart_item_service import add_item_to_cart, remove_item_from_cart

router = APIRouter(prefix="/carts", tags=["carts"])


@router.post(
    "/{cart_id}/items",
    response_model=CartItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_cart_item(cart_id: UUID, payload: CartItemCreateRequest) -> CartItemResponse:
    item = add_item_to_cart(cart_id, payload)
    return CartItemResponse(**item)


@router.delete(
    "/{cart_id}/items/{cart_item_id}",
    response_model=CartItemDeleteResponse,
    status_code=status.HTTP_200_OK,
)
def delete_cart_item(cart_id: UUID, cart_item_id: UUID) -> CartItemDeleteResponse:
    result = remove_item_from_cart(cart_id, cart_item_id)
    return CartItemDeleteResponse(**result)