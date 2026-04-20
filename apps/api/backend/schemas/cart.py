from datetime import datetime
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