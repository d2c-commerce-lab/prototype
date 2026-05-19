import { apiClient } from "./apiClient";
import type { UserCouponWalletResponse } from "../types/coupon";

export function getUserCoupons(userId: string) {
  return apiClient<UserCouponWalletResponse>(`/users/${userId}/coupons`);
}