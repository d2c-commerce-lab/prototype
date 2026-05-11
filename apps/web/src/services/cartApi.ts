import { apiClient } from "./apiClient";
import type { Cart, CartItem } from "../types/cart";

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

export function addCartItem(cartId: string, payload: AddCartItemRequest) {
  return apiClient<CartItem>(`/carts/${cartId}/items`, {
    method: "POST",
    body: payload,
  });
}