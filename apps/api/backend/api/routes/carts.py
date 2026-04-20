from fastapi import APIRouter, status

from backend.schemas.cart import CartCreateRequest, CartResponse
from backend.services.cart_service import create_or_get_active_cart

router = APIRouter(prefix="/carts", tags=["carts"])


@router.post("", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
def create_cart(payload: CartCreateRequest) -> CartResponse:
    cart = create_or_get_active_cart(payload)
    return CartResponse(**cart)