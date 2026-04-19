from typing import Any
from uuid import UUID

from sqlalchemy import text

from backend.db.connection import engine


def get_products(category_id: UUID | None = None) -> list[dict[str, Any]]:
    base_query = """
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
        WHERE is_active = TRUE
          AND product_status IN ('on_sale', 'out_of_stock')
    """

    params: dict[str, Any] = {}

    if category_id is not None:
        base_query += " AND category_id = :category_id"
        params["category_id"] = category_id

    base_query += " ORDER BY product_name ASC"

    query = text(base_query)

    with engine.connect() as connection:
        result = connection.execute(query, params)
        rows = result.mappings().all()

    return [dict(row) for row in rows]