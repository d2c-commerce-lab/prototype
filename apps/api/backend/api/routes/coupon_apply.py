from uuid import UUID

from fastapi import APIRouter, status

from backend.schemas.coupon_apply import CouponApplyRequest, CouponApplyResponse
from backend.services.coupon_service import apply_coupon_to_cart

router = APIRouter(prefix="/carts", tags=["checkout"])


@router.post(
    "/{cart_id}/coupon",
    response_model=CouponApplyResponse,
    status_code=status.HTTP_200_OK,
)
def apply_coupon(cart_id: UUID, payload: CouponApplyRequest) -> CouponApplyResponse:
    result = apply_coupon_to_cart(cart_id, payload)
    return CouponApplyResponse(**result)