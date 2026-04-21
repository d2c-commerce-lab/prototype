from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class CartCreateRequest(BaseModel):
    user_id: UUID


class CartResponse(BaseModel):
    cart_id: UUID
    user_id: UUID
    cart_status: str
    created_at: datetime
    updated_at: datetime
    checked_out_at: datetime | None = None


class CartItemSummaryResponse(BaseModel):
    cart_item_id: UUID
    product_id: UUID
    product_name: str
    quantity: int
    unit_price: Decimal
    currency: str
    line_total: Decimal
    added_at: datetime
    updated_at: datetime


class CartDetailResponse(BaseModel):
    cart_id: UUID
    user_id: UUID
    cart_status: str
    created_at: datetime
    updated_at: datetime
    checked_out_at: datetime | None = None
    total_items: int
    total_quantity: int
    total_amount: Decimal
    currency: str | None = None
    items: list[CartItemSummaryResponse]