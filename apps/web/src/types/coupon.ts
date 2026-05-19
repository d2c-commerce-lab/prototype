export type UserCoupon = {
  coupon_id: string;
  campaign_id?: string | null;
  coupon_name: string;
  coupon_type: "percentage" | "fixed_amount" | string;
  discount_value: string | number;
  minimum_order_amount: string | number;
  valid_start_at: string;
  valid_end_at: string;
  coupon_status: string;
};

export type UsedCoupon = UserCoupon & {
  used_order_id: string;
  used_at: string;
  payment_id?: string | null;
};

export type UserCouponWalletResponse = {
  user_id: string;
  available_coupons: UserCoupon[];
  used_coupons: UsedCoupon[];
};