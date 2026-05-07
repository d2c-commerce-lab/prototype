from typing import List
from uuid import UUID

from fastapi import APIRouter, Query

from backend.schemas.product import ProductResponse
from backend.services.product_service import get_products

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=List[ProductResponse])
def list_products(
    category_id: UUID | None = Query(default=None)
) -> list[ProductResponse]:
    products = get_products(category_id=category_id)
    return [ProductResponse(**product) for product in products]