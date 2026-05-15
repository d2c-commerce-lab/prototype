import { apiClient } from "./apiClient";
import type {
  CheckoutSummary,
  CouponApplyRequest,
  CouponApplyResponse,
  OrderCreateRequest,
  OrderCreateResponse,
  PaymentSimulationRequest,
  PaymentSimulationResponse,
} from "../types/checkout";

export function enterCheckout(cartId: string) {
  return apiClient<CheckoutSummary>(`/checkout/${cartId}`);
}

export function applyCoupon(cartId: string, couponName: string) {
  return apiClient<CouponApplyResponse>(`/carts/${cartId}/apply-coupon`, {
    method: "POST",
    body: {
      coupon_name: couponName,
    },
  });
}

export function createOrder(payload: OrderCreateRequest) {
  return apiClient<OrderCreateResponse>("/orders", {
    method: "POST",
    body: payload,
  });
}

export function simulatePayment(payload: PaymentSimulationRequest) {
  return apiClient<PaymentSimulationResponse>("/payments/simulate", {
    method: "POST",
    body: payload,
  });
}