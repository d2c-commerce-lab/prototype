from fastapi import APIRouter
from typing import List

from backend.schemas.category import CategoryResponse
from backend.services.category_service import get_active_categories

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=List[CategoryResponse])
def list_categories() -> list[CategoryResponse]:
    categories = get_active_categories()
    return [CategoryResponse(**category) for category in categories]