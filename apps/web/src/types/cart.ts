export type Cart = {
  cart_id: string;
  user_id: string;
  cart_status: string;
  total_items?: number;
  total_quantity?: number;
  total_amount?: string | number;
  currency?: string;
};

export type CartItem = {
  cart_item_id: string;
  cart_id: string;
  product_id: string;
  product_name?: string;
  brand_name?: string | null;
  quantity: number;
  unit_price: string | number;
  line_amount?: string | number;
  line_total?: string | number;
  currency: string;
};

export type CartDetail = Cart & {
  items?: CartItem[];
  cart_items?: CartItem[];
};