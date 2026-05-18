export type ReviewCreateRequest = {
  user_id: string;
  product_id: string;
  order_item_id: string;
  rating: number;
  review_title: string;
  review_content: string;
};

export type ReviewCreateResponse = {
  review_id: string;
  user_id: string;
  product_id: string;
  order_item_id: string;
  rating: number;
  review_title: string;
  review_content: string;
  review_status: string;
  created_at: string;
  updated_at: string;
  message: string;
};

export type ProductReviewItem = {
  review_id: string;
  user_id: string;
  product_id: string;
  order_item_id: string;
  rating: number;
  review_title: string;
  review_content: string;
  review_status: string;
  created_at: string;
  updated_at?: string | null;
  user_name?: string | null;
};

export type ProductReviewListResponse = {
  product_id: string;
  total_reviews: number;
  average_rating?: string | number | null;
  reviews: ProductReviewItem[];
};