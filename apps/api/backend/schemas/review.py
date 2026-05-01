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


class ReviewUpdateRequest(BaseModel):
    user_id: UUID
    rating: int | None = Field(default=None, ge=1, le=5)
    review_title: str | None = Field(default=None, min_length=1, max_length=200)
    review_content: str | None = Field(default=None, min_length=1, max_length=2000)


class ReviewDeleteRequest(BaseModel):
    user_id: UUID


class ReviewResponse(BaseModel):
    review_id: UUID
    user_id: UUID
    product_id: UUID
    order_item_id: UUID
    rating: int
    review_title: str
    review_content: str | None = None
    review_status: str
    created_at: datetime
    updated_at: datetime


class ReviewCreateResponse(ReviewResponse):
    message: str


class ReviewUpdateResponse(ReviewResponse):
    message: str


class ReviewDeleteResponse(BaseModel):
    review_id: UUID
    user_id: UUID
    review_status: str
    updated_at: datetime
    message: str