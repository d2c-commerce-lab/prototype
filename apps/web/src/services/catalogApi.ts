import { apiClient } from "./apiClient";
import type { Category, Product } from "../types/catalog";

export function getCategories() {
  return apiClient<Category[]>("/categories");
}

export function getProducts(categoryId?: string) {
  const query = categoryId ? `?category_id=${categoryId}` : "";
  return apiClient<Product[]>(`/products${query}`);
}