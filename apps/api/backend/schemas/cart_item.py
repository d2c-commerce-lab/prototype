from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class CartItemCreateRequest(BaseModel):
    product_id: UUID
    quantity: int = Field(ge=1, le=99)


class CartItemResponse(BaseModel):
    cart_item_id: UUID
    cart_id: UUID
    product_id: UUID
    quantity: int
    unit_price: Decimal
    currency: str
    added_at: datetime
    updated_at: datetime


class CartItemDeleteResponse(BaseModel):
    cart_item_id: UUID
    cart_id: UUID
    message: str


class CartItemQuantityUpdateRequest(BaseModel):
    quantity: int = Field(ge=1, le=99)