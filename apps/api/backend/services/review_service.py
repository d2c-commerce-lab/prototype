from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import text

from backend.db.connection import engine
from backend.schemas.review import (
    ReviewCreateRequest,
    ReviewDeleteRequest,
    ReviewUpdateRequest,
)


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


def update_review(review_id: str, payload: ReviewUpdateRequest) -> dict[str, Any]:
    review_query = text("""
        SELECT
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
        FROM reviews
        WHERE review_id = :review_id
        LIMIT 1
    """)

    update_review_query = text("""
        UPDATE reviews
        SET
            rating = :rating,
            review_title = :review_title,
            review_content = :review_content,
            updated_at = CURRENT_TIMESTAMP
        WHERE review_id = :review_id
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
        review = connection.execute(
            review_query,
            {"review_id": review_id},
        ).mappings().first()

        if review is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found",
            )

        if str(review["user_id"]) != str(payload.user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own review",
            )

        if review["review_status"] == "deleted":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Deleted review cannot be updated",
            )

        updated_review = connection.execute(
            update_review_query,
            {
                "review_id": review_id,
                "rating": payload.rating if payload.rating is not None else review["rating"],
                "review_title": (
                    payload.review_title
                    if payload.review_title is not None
                    else review["review_title"]
                ),
                "review_content": (
                    payload.review_content
                    if payload.review_content is not None
                    else review["review_content"]
                ),
            },
        ).mappings().first()

        if updated_review is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update review",
            )

    return {
        "review_id": updated_review["review_id"],
        "user_id": updated_review["user_id"],
        "product_id": updated_review["product_id"],
        "order_item_id": updated_review["order_item_id"],
        "rating": updated_review["rating"],
        "review_title": updated_review["review_title"],
        "review_content": updated_review["review_content"],
        "review_status": updated_review["review_status"],
        "created_at": updated_review["created_at"],
        "updated_at": updated_review["updated_at"],
        "message": "Review updated successfully",
    }


def delete_review(review_id: str, payload: ReviewDeleteRequest) -> dict[str, Any]:
    review_query = text("""
        SELECT
            review_id,
            user_id,
            review_status
        FROM reviews
        WHERE review_id = :review_id
        LIMIT 1
    """)

    delete_review_query = text("""
        UPDATE reviews
        SET
            review_status = 'deleted',
            updated_at = CURRENT_TIMESTAMP
        WHERE review_id = :review_id
        RETURNING
            review_id,
            user_id,
            review_status,
            updated_at
    """)

    with engine.begin() as connection:
        review = connection.execute(
            review_query,
            {"review_id": review_id},
        ).mappings().first()

        if review is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found",
            )

        if str(review["user_id"]) != str(payload.user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own review",
            )

        if review["review_status"] == "deleted":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Review is already deleted",
            )

        deleted_review = connection.execute(
            delete_review_query,
            {"review_id": review_id},
        ).mappings().first()

        if deleted_review is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete review",
            )

    return {
        "review_id": deleted_review["review_id"],
        "user_id": deleted_review["user_id"],
        "review_status": deleted_review["review_status"],
        "updated_at": deleted_review["updated_at"],
        "message": "Review deleted successfully",
    }