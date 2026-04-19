from typing import Any
from uuid import UUID

from sqlalchemy import text

from backend.db.connection import engine


def get_product_detail(product_id: UUID) -> dict[str, Any] | None:
    query = text("""
        SELECT
            product_id,
            category_id,
            product_name,
            product_status,
            list_price,
            sale_price,
            currency,
            brand_name,
            is_active
        FROM products
        WHERE product_id = :product_id
        AND is_active = TRUE
        LIMIT 1  
    """)

    with engine.connect() as connection:
        result = connection.execute(query, {"product_id": product_id})
        row = result.mappings().first()

    if row is None:
        return None
    
    return dict(row)