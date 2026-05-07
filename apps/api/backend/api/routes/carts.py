from uuid import UUID

from fastapi import APIRouter, status

from backend.schemas.cart import CartCreateRequest, CartDetailResponse, CartResponse
from backend.services.cart_service import create_or_get_active_cart, get_cart_detail

router = APIRouter(prefix="/carts", tags=["carts"])


@router.post("", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
def create_cart(payload: CartCreateRequest) -> CartResponse:
    cart = create_or_get_active_cart(payload)
    return CartResponse(**cart)


@router.get("/{cart_id}", response_model=CartDetailResponse, status_code=status.HTTP_200_OK)
def get_cart(cart_id: UUID) -> CartDetailResponse:
    cart = get_cart_detail(cart_id)
    return CartDetailResponse(**cart)