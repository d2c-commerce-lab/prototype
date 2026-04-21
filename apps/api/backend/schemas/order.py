from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class OrderCreateRequest(BaseModel):
    cart_id: UUID
    coupon_name: str | None = None


class OrderItemResponse(BaseModel):
    order_item_id: UUID
    product_id: UUID
    product_name: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal
    currency: str


class OrderCreateResponse(BaseModel):
    order_id: UUID
    user_id: UUID
    cart_id: UUID
    order_status: str
    subtotal_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    currency: str | None = None
    coupon_name: str | None = None
    ordered_at: datetime
    items: list[OrderItemResponse]
    message: str