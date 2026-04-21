from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class OrderHistoryItemResponse(BaseModel):
    order_item_id: UUID
    product_id: UUID
    product_name: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal
    currency: str


class OrderHistorySummaryResponse(BaseModel):
    order_id: UUID
    cart_id: UUID | None = None
    order_status: str
    payment_status: str | None = None
    subtotal_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    currency: str | None = None
    coupon_name: str | None = None
    ordered_at: datetime
    items: list[OrderHistoryItemResponse]


class OrderHistoryListResponse(BaseModel):
    user_id: UUID
    total_orders: int
    orders: list[OrderHistorySummaryResponse]