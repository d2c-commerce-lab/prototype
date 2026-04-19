from uuid import UUID

from fastapi import APIRouter, HTTPException

from backend.schemas.product_detail import ProductDetailResponse
from backend.services.product_detail_service import get_product_detail

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/{product_id}", response_model=ProductDetailResponse)
def retrieve_product_detail(product_id: UUID) -> ProductDetailResponse:
    product = get_product_detail(product_id)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return ProductDetailResponse(**product)
