from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class CouponApplyRequest(BaseModel):
    coupon_name: str = Field(min_length=1, max_length=100)


class AppliedCouponResponse(BaseModel):
    coupon_id: UUID
    campaign_id: UUID | None = None
    coupon_name: str
    coupon_type: str
    discount_value: Decimal
    minimum_order_amount: Decimal
    coupon_status: str
    valid_start_at: datetime
    valid_end_at: datetime


class CouponApplyResponse(BaseModel):
    cart_id: UUID
    coupon: AppliedCouponResponse
    total_amount: Decimal
    discount_amount: Decimal
    final_amount: Decimal
    currency: str | None = None
    message: str