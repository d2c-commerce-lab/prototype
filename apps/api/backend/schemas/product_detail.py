from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class ProductDetailResponse(BaseModel):
    product_id: UUID
    category_id: UUID
    product_name: str
    product_status: str
    list_price: Decimal
    sale_price: Decimal
    currency: str
    brand_name: str | None = None
    is_active: bool