import type { CartItem } from "./cart";

export type CheckoutSummary = {
  cart_id: string;
  user_id: string;
  items: CartItem[];
  total_items: number;
  total_quantity: number;
  total_amount?: string | number;
  original_amount?: string | number;
  discount_amount?: string | number;
  final_amount?: string | number;
  currency: string;
  applied_coupon_id?: string | null;
  applied_coupon_code?: string | null;
};

export type CouponApplyRequest = {
  coupon_name: string;
};

export type CouponSummary = {
  coupon_id: string;
  campaign_id?: string | null;
  coupon_name: string;
  coupon_type?: string;
  discount_value?: string | number;
  minimum_order_amount?: string | number;
  coupon_status?: string;
  valid_start_at?: string;
  valid_end_at?: string;
};

export type CouponApplyResponse = {
  cart_id: string;
  coupon?: CouponSummary;
  coupon_id?: string;
  coupon_name?: string;
  coupon_code?: string;
  total_amount?: string | number;
  original_amount?: string | number;
  discount_amount: string | number;
  final_amount: string | number;
  currency: string;
  message: string;
};

export type OrderCreateRequest = {
  cart_id: string;
  coupon_name?: string | null;
};

export type OrderCreateResponse = {
  order_id: string;
  user_id: string;
  cart_id: string;
  order_status: string;
  total_amount: string | number;
  discount_amount?: string | number;
  final_amount?: string | number;
  currency: string;
  created_at: string;
};

export type PaymentSimulationRequest = {
  order_id: string;
  payment_method: string;
  simulate_result: "success" | "failed";
};

export type PaymentSimulationResponse = {
  payment_id: string;
  order_id: string;
  payment_method: string;
  payment_status: string;
  requested_amount: string | number;
  approved_amount: string | number;
  failed_reason?: string | null;
  paid_at?: string | null;
  created_at: string;
  message: string;
};