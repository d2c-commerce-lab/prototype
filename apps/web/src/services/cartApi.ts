import { apiClient } from "./apiClient";
import type { Cart, CartDetail, CartItem } from "../types/cart";

type CreateCartRequest = {
  user_id: string;
};

type AddCartItemRequest = {
  product_id: string;
  quantity: number;
};

export function createCart(payload: CreateCartRequest) {
  return apiClient<Cart>("/carts", {
    method: "POST",
    body: payload,
  });
}

export function getCart(cartId: string) {
  return apiClient<CartDetail>(`/carts/${cartId}`);
}

export function addCartItem(cartId: string, payload: AddCartItemRequest) {
  return apiClient<CartItem>(`/carts/${cartId}/items`, {
    method: "POST",
    body: payload,
  });
}

export function updateCartItemQuantity(
  cartId: string,
  cartItemId: string,
  quantity: number,
) {
  return apiClient<CartItem>(`/carts/${cartId}/items/${cartItemId}`, {
    method: "PATCH",
    body: {
      quantity,
    },
  });
}

export function removeCartItem(cartId: string, cartItemId: string) {
  return apiClient<{ message: string }>(`/carts/${cartId}/items/${cartItemId}`, {
    method: "DELETE",
  });
}