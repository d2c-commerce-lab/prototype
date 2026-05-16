export type OrderItem = {
  order_item_id: string;
  product_id: string;
  product_name?: string;
  quantity: number;
  unit_price: string | number;
  discount_amount?: string | number;
  final_item_amount?: string | number;
  line_total?: string | number;
  currency: string;
};

export type OrderHistoryItem = {
  order_history_id: string;
  history_event_type: string;
  history_event_at: string;
  order_id: string;
  user_id: string;
  cart_id?: string;
  coupon_name?: string | null;
  order_status: string;
  payment_id?: string | null;
  payment_status?: string | null;
  subtotal_amount?: string | number;
  discount_amount?: string | number;
  total_amount: string | number;
  currency: string;
  ordered_at?: string;
  created_at?: string;
  updated_at?: string;
  items: OrderItem[];
};

export type OrderHistoryResponse = {
  user_id: string;
  total_orders: number;
  orders: OrderHistoryItem[];
};