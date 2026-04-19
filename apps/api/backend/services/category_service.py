from sqlalchemy import text

from backend.db.connection import engine


def get_active_categories() -> list[dict]:
    query = text("""
        SELECT
            category_id,
            category_name,
            category_depth,
            category_status
        FROM categories
        WHERE category_status = 'active'
        ORDER BY category_name ASC
    """)

    with engine.connect() as connection:
        result = connection.execute(query)
        rows = result.mappings().all()

    return [dict(row) for row in rows]