from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ReviewCreateRequest(BaseModel):
    user_id: UUID
    product_id: UUID
    order_item_id: UUID
    rating: int = Field(ge=1, le=5)
    review_title: str = Field(min_length=1, max_length=200)
    review_content: str = Field(min_length=1, max_length=2000)


class ReviewCreateResponse(BaseModel):
    review_id: UUID
    user_id: UUID
    product_id: UUID
    order_item_id: UUID
    rating: int
    review_title: str
    review_content: str
    review_status: str
    created_at: datetime
    updated_at: datetime
    message: str