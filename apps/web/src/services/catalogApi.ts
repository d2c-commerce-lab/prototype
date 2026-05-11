import { apiClient } from "./apiClient";
import type { Category, Product, ProductDetail } from "../types/catalog";

export function getCategories() {
  return apiClient<Category[]>("/categories");
}

export function getProducts(categoryId?: string) {
  const query = categoryId ? `?category_id=${categoryId}` : "";
  return apiClient<Product[]>(`/products${query}`);
}

export function getProductDetail(productId: string) {
  return apiClient<ProductDetail>(`/products/${productId}`);
}