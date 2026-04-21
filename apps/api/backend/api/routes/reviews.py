from fastapi import APIRouter, status

from backend.schemas.review import ReviewCreateRequest, ReviewCreateResponse
from backend.services.review_service import create_review

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=ReviewCreateResponse, status_code=status.HTTP_201_CREATED)
def create_product_review(payload: ReviewCreateRequest) -> ReviewCreateResponse:
    result = create_review(payload)
    return ReviewCreateResponse(**result)