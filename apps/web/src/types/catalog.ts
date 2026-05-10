export type Category = {
  category_id: string;
  parent_category_id: string | null;
  category_name: string;
  category_depth: number;
  category_status: string;
};

export type Product = {
  product_id: string;
  category_id: string;
  product_name: string;
  product_status: string;
  list_price: string | number;
  sale_price: string | number;
  currency: string;
  brand_name: string | null;
  is_active: boolean;
};