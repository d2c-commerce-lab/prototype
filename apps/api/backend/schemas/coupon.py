from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class UserAvailableCouponResponse(BaseModel):
    coupon_id: UUID
    campaign_id: UUID | None = None
    coupon_name: str
    coupon_type: str
    discount_value: Decimal
    minimum_order_amount: Decimal
    coupon_status: str
    valid_start_at: datetime
    valid_end_at: datetime


class UserUsedCouponResponse(BaseModel):
    coupon_id: UUID
    campaign_id: UUID | None = None
    coupon_name: str
    coupon_type: str
    discount_value: Decimal
    minimum_order_amount: Decimal
    coupon_status: str
    valid_start_at: datetime
    valid_end_at: datetime
    used_order_id: UUID
    used_at: datetime
    payment_id: UUID | None = None


class UserCouponWalletResponse(BaseModel):
    user_id: UUID
    available_coupons: list[UserAvailableCouponResponse]
    used_coupons: list[UserUsedCouponResponse]