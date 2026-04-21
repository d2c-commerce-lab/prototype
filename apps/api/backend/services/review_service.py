from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import text

from backend.db.connection import engine
from backend.schemas.review import ReviewCreateRequest


def create_review(payload: ReviewCreateRequest) -> dict[str, Any]:
    user_query = text("""
        SELECT
            user_id
        FROM users
        WHERE user_id = :user_id
        LIMIT 1
    """)

    product_query = text("""
        SELECT
            product_id,
            is_active,
            product_status
        FROM products
        WHERE product_id = :product_id
        LIMIT 1
    """)

    purchase_query = text("""
        SELECT
            oi.order_item_id
        FROM orders o
        JOIN order_items oi
          ON oi.order_id = o.order_id
        WHERE o.user_id = :user_id
          AND oi.product_id = :product_id
          AND oi.order_item_id = :order_item_id
          AND o.order_status = 'paid'
        LIMIT 1
    """)

    duplicate_review_query = text("""
        SELECT
            review_id
        FROM reviews
        WHERE order_item_id = :order_item_id
        LIMIT 1
    """)

    insert_review_query = text("""
        INSERT INTO reviews (
            user_id,
            product_id,
            order_item_id,
            rating,
            review_title,
            review_content,
            review_status,
            created_at,
            updated_at
        )
        VALUES (
            :user_id,
            :product_id,
            :order_item_id,
            :rating,
            :review_title,
            :review_content,
            'visible',
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        )
        RETURNING
            review_id,
            user_id,
            product_id,
            order_item_id,
            rating,
            review_title,
            review_content,
            review_status,
            created_at,
            updated_at
    """)

    with engine.begin() as connection:
        user = connection.execute(
            user_query,
            {"user_id": payload.user_id},
        ).mappings().first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        product = connection.execute(
            product_query,
            {"product_id": payload.product_id},
        ).mappings().first()

        if product is None or not product["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        purchase = connection.execute(
            purchase_query,
            {
                "user_id": payload.user_id,
                "product_id": payload.product_id,
                "order_item_id": payload.order_item_id,
            },
        ).mappings().first()

        if purchase is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Review can only be created for purchased products",
            )

        duplicate_review = connection.execute(
            duplicate_review_query,
            {
                "order_item_id": payload.order_item_id,
            },
        ).mappings().first()

        if duplicate_review is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Review already exists for this order item",
            )

        created_review = connection.execute(
            insert_review_query,
            {
                "user_id": payload.user_id,
                "product_id": payload.product_id,
                "order_item_id": payload.order_item_id,
                "rating": payload.rating,
                "review_title": payload.review_title,
                "review_content": payload.review_content,
            },
        ).mappings().first()

        if created_review is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create review",
            )

    return {
        "review_id": created_review["review_id"],
        "user_id": created_review["user_id"],
        "product_id": created_review["product_id"],
        "order_item_id": created_review["order_item_id"],
        "rating": created_review["rating"],
        "review_title": created_review["review_title"],
        "review_content": created_review["review_content"],
        "review_status": created_review["review_status"],
        "created_at": created_review["created_at"],
        "updated_at": created_review["updated_at"],
        "message": "Review created successfully",
    }