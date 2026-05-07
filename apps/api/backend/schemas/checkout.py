from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, EmailStr


class CheckoutCartItemResponse(BaseModel):
    cart_item_id: UUID
    product_id: UUID
    product_name: str
    quantity: int
    unit_price: Decimal
    currency: str
    line_total: Decimal
    added_at: datetime
    updated_at: datetime


class CheckoutUserSummaryResponse(BaseModel):
    user_id: UUID
    email: EmailStr
    user_name: str
    user_status: str
    marketing_opt_in_yn: bool


class CheckoutCouponSummaryResponse(BaseModel):
    coupon_id: UUID
    campaign_id: UUID | None = None
    coupon_name: str
    coupon_type: str
    discount_value: Decimal
    minimum_order_amount: Decimal
    coupon_status: str
    valid_start_at: datetime
    valid_end_at: datetime


class CheckoutResponse(BaseModel):
    cart_id: UUID
    user_id: UUID
    cart_status: str
    total_items: int
    total_quantity: int
    total_amount: Decimal
    currency: str | None = None
    items: list[CheckoutCartItemResponse]
    user: CheckoutUserSummaryResponse
    available_coupons: list[CheckoutCouponSummaryResponse]