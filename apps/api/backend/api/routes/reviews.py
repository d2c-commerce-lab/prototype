from fastapi import APIRouter, status

from backend.schemas.review import (
    ReviewCreateRequest,
    ReviewCreateResponse,
    ReviewDeleteRequest,
    ReviewDeleteResponse,
    ReviewUpdateRequest,
    ReviewUpdateResponse,
)
from backend.services.review_service import create_review, delete_review, update_review

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=ReviewCreateResponse, status_code=status.HTTP_201_CREATED)
def create_product_review(payload: ReviewCreateRequest) -> ReviewCreateResponse:
    result = create_review(payload)
    return ReviewCreateResponse(**result)


@router.patch(
    "/{review_id}",
    response_model=ReviewUpdateResponse,
    status_code=status.HTTP_200_OK,
)
def update_product_review(
    review_id: str,
    payload: ReviewUpdateRequest,
) -> ReviewUpdateResponse:
    result = update_review(review_id, payload)
    return ReviewUpdateResponse(**result)


@router.delete(
    "/{review_id}",
    response_model=ReviewDeleteResponse,
    status_code=status.HTTP_200_OK,
)
def delete_product_review(
    review_id: str,
    payload: ReviewDeleteRequest,
) -> ReviewDeleteResponse:
    result = delete_review(review_id, payload)
    return ReviewDeleteResponse(**result)