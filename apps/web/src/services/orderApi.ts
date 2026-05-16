import { apiClient } from "./apiClient";
import type { OrderHistoryResponse } from "../types/order";

export function getOrderHistory(userId: string) {
  return apiClient<OrderHistoryResponse>(`/orders?user_id=${userId}`);
}