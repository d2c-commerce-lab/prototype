from uuid import UUID

from fastapi import APIRouter, status

from backend.schemas.coupon import UserCouponWalletResponse
from backend.services.coupon_service import list_user_coupons

router = APIRouter(prefix="/users", tags=["coupons"])


@router.get(
    "/{user_id}/coupons",
    response_model=UserCouponWalletResponse,
    status_code=status.HTTP_200_OK,
)
def get_user_coupons(user_id: UUID) -> UserCouponWalletResponse:
    result = list_user_coupons(user_id)
    return UserCouponWalletResponse(**result)