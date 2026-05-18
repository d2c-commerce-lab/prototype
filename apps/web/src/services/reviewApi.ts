import { apiClient } from "./apiClient";
import type {
  ProductReviewListResponse,
  ReviewCreateRequest,
  ReviewCreateResponse,
} from "../types/review";

export function createReview(payload: ReviewCreateRequest) {
  return apiClient<ReviewCreateResponse>("/reviews", {
    method: "POST",
    body: payload,
  });
}

export function getProductReviews(productId: string) {
  return apiClient<ProductReviewListResponse>(
    `/reviews/products/${productId}/reviews`,
  );
}