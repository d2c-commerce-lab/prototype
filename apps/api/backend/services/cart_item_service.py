from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import text

from backend.db.connection import engine
from backend.schemas.cart_item import CartItemCreateRequest


def add_item_to_cart(cart_id: UUID, payload: CartItemCreateRequest) -> dict[str, Any]:
    cart_query = text("""
        SELECT
            cart_id,
            cart_status
        FROM carts
        WHERE cart_id = :cart_id
          AND cart_status = 'active'
        LIMIT 1
    """)

    product_query = text("""
        SELECT
            product_id,
            sale_price,
            currency,
            is_active,
            product_status
        FROM products
        WHERE product_id = :product_id
        LIMIT 1
    """)

    existing_item_query = text("""
        SELECT
            cart_item_id,
            cart_id,
            product_id,
            quantity,
            unit_price,
            currency,
            added_at,
            updated_at
        FROM cart_items
        WHERE cart_id = :cart_id
          AND product_id = :product_id
        LIMIT 1
    """)

    insert_item_query = text("""
        INSERT INTO cart_items (
            cart_id,
            product_id,
            quantity,
            unit_price,
            currency,
            added_at,
            updated_at
        )
        VALUES (
            :cart_id,
            :product_id,
            :quantity,
            :unit_price,
            :currency,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        )
        RETURNING
            cart_item_id,
            cart_id,
            product_id,
            quantity,
            unit_price,
            currency,
            added_at,
            updated_at
    """)

    update_item_query = text("""
        UPDATE cart_items
        SET
            quantity = quantity + :quantity,
            updated_at = CURRENT_TIMESTAMP
        WHERE cart_item_id = :cart_item_id
        RETURNING
            cart_item_id,
            cart_id,
            product_id,
            quantity,
            unit_price,
            currency,
            added_at,
            updated_at
    """)

    with engine.begin() as connection:
        cart = connection.execute(
            cart_query,
            {"cart_id": cart_id},
        ).mappings().first()

        if cart is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active cart not found",
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

        if product["product_status"] not in ("on_sale", "out_of_stock"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        existing_item = connection.execute(
            existing_item_query,
            {
                "cart_id": cart_id,
                "product_id": payload.product_id,
            },
        ).mappings().first()

        if existing_item is not None:
            updated_item = connection.execute(
                update_item_query,
                {
                    "cart_item_id": existing_item["cart_item_id"],
                    "quantity": payload.quantity,
                },
            ).mappings().first()

            if updated_item is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update cart item",
                )

            return {
                "cart_item_id": updated_item["cart_item_id"],
                "cart_id": updated_item["cart_id"],
                "product_id": updated_item["product_id"],
                "quantity": updated_item["quantity"],
                "unit_price": updated_item["unit_price"],
                "currency": updated_item["currency"],
                "added_at": updated_item["added_at"],
                "updated_at": updated_item["updated_at"],
            }

        created_item = connection.execute(
            insert_item_query,
            {
                "cart_id": cart_id,
                "product_id": payload.product_id,
                "quantity": payload.quantity,
                "unit_price": product["sale_price"],
                "currency": product["currency"],
            },
        ).mappings().first()

        if created_item is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add item to cart",
            )

        return {
            "cart_item_id": created_item["cart_item_id"],
            "cart_id": created_item["cart_id"],
            "product_id": created_item["product_id"],
            "quantity": created_item["quantity"],
            "unit_price": created_item["unit_price"],
            "currency": created_item["currency"],
            "added_at": created_item["added_at"],
            "updated_at": created_item["updated_at"],
        }


def remove_item_from_cart(cart_id: UUID, cart_item_id: UUID) -> dict[str, Any]:
    cart_query = text("""
        SELECT
            cart_id
        FROM carts
        WHERE cart_id = :cart_id
          AND cart_status = 'active'
        LIMIT 1
    """)

    delete_query = text("""
        DELETE FROM cart_items
        WHERE cart_item_id = :cart_item_id
          AND cart_id = :cart_id
        RETURNING
            cart_item_id,
            cart_id
    """)

    with engine.begin() as connection:
        cart = connection.execute(
            cart_query,
            {"cart_id": cart_id},
        ).mappings().first()

        if cart is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active cart not found",
            )

        deleted_item = connection.execute(
            delete_query,
            {
                "cart_id": cart_id,
                "cart_item_id": cart_item_id,
            },
        ).mappings().first()

        if deleted_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found",
            )

        return {
            "cart_item_id": deleted_item["cart_item_id"],
            "cart_id": deleted_item["cart_id"],
            "message": "Cart item removed successfully",
        }