import { useEffect, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { addCartItem, createCart } from "../../services/cartApi";
import { getProductDetail } from "../../services/catalogApi";
import { recordUserBehaviorEvent } from "../../services/eventLogApi";
import { getProductReviews } from "../../services/reviewApi";
import {
  clearStoredCartId,
  clearStoredPendingOrder,
  getStoredCartId,
  getStoredUser,
  setStoredCartId,
} from "../../stores/userStore";
import type { ProductDetail } from "../../types/catalog";
import type { ProductReviewItem, ReviewCreateResponse } from "../../types/review";

type ProductDetailLocationState = {
  createdReview?: ReviewCreateResponse;
};

function formatPrice(value: string | number, currency: string) {
  const numericValue = Number(value);

  if (Number.isNaN(numericValue)) {
    return `${value} ${currency}`;
  }

  return new Intl.NumberFormat("ko-KR", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(numericValue);
}

function formatReviewerName(userName?: string | null) {
  const normalizedUserName = userName?.trim();

  return normalizedUserName ? `${normalizedUserName}님` : "구매자님";
}

function parseUtcNaiveDateTime(value: string) {
  const hasTimezone = /([zZ]|[+-]\d{2}:\d{2})$/.test(value);

  if (hasTimezone) {
    return new Date(value);
  }

  const normalizedValue = value.replace(/\.(\d{3})\d+/, ".$1");

  return new Date(`${normalizedValue}Z`);
}

function formatReviewDateTime(value?: string | null) {
  if (!value) {
    return "-";
  }

  const date = parseUtcNaiveDateTime(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("ko-KR", {
    timeZone: "Asia/Seoul",
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function getReviewRecommendationLabel(reviewContent: string) {
  const firstLine = reviewContent.split("\n")[0]?.trim();

  if (firstLine.startsWith("상품 추천 여부:")) {
    return firstLine;
  }

  return "상품 추천 여부: 미기록";
}

function getReviewDetailContent(reviewContent: string) {
  const lines = reviewContent.split("\n");
  const firstLine = lines[0]?.trim();

  if (firstLine.startsWith("상품 추천 여부:")) {
    return lines.slice(1).join("\n").trim();
  }

  return reviewContent;
}

export function ProductDetailPage() {
  const { productId } = useParams();

  const [product, setProduct] = useState<ProductDetail | null>(null);
  const [quantity, setQuantity] = useState<number>(1);
  const [isLoading, setIsLoading] = useState(true);
  const [isAddingToCart, setIsAddingToCart] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [cartMessage, setCartMessage] = useState<string | null>(null);
  const [cartErrorMessage, setCartErrorMessage] = useState<string | null>(null);

  const user = getStoredUser();

  const location = useLocation();
  const locationState = location.state as ProductDetailLocationState | null;

  const [reviews, setReviews] = useState<ProductReviewItem[]>([]);
  const [reviewSummary, setReviewSummary] = useState<{
    totalReviews: number;
    averageRating: string | number | null;
  }>({
    totalReviews: 0,
    averageRating: null,
  });
  const [reviewErrorMessage, setReviewErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    async function loadProductDetail() {
      if (!productId) {
        setErrorMessage("상품 식별자를 확인할 수 없습니다.");
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setErrorMessage(null);

        const productData = await getProductDetail(productId);
        setProduct(productData);
      } catch {
        setErrorMessage("상품 상세 정보를 불러오지 못했습니다.");
      } finally {
        setIsLoading(false);
      }
    }

    loadProductDetail();
  }, [productId]);

  useEffect(() => {
    if (!product) {
      return;
    }

    void recordUserBehaviorEvent({
      event_name: "product_detail_viewed",
      user_id: user?.user_id ?? null,
      session_id: null,
      entity_type: "product",
      entity_id: product.product_id,
      properties: {
        page_path: window.location.pathname,
        product_id: product.product_id,
        product_name: product.product_name,
        source_page: "product_detail",
      },
    });
  }, [product?.product_id, user?.user_id]);

  useEffect(() => {
    async function loadProductReviews() {
      if (!productId) {
        return;
      }

      try {
        setReviewErrorMessage(null);

        const reviewData = await getProductReviews(productId);

        setReviews(reviewData.reviews);
        setReviewSummary({
          totalReviews: reviewData.total_reviews,
          averageRating: reviewData.average_rating ?? null,
        });
      } catch {
        setReviewErrorMessage("상품 리뷰를 불러오지 못했습니다.");
      }
    }

    loadProductReviews();
  }, [productId]);

  useEffect(() => {
    const createdReview = locationState?.createdReview;

    if (!createdReview) {
      return;
    }

    setReviews((currentReviews) => {
      const alreadyExists = currentReviews.some(
        (review) => review.review_id === createdReview.review_id,
      );

      if (alreadyExists) {
        return currentReviews;
      }

      return [createdReview, ...currentReviews];
    });

    setReviewSummary((currentSummary) => ({
      totalReviews: currentSummary.totalReviews + 1,
      averageRating: currentSummary.averageRating,
    }));
  }, [locationState?.createdReview]);

  const handleDecreaseQuantity = () => {
    setQuantity((currentQuantity) => Math.max(1, currentQuantity - 1));
  };

  const handleIncreaseQuantity = () => {
    setQuantity((currentQuantity) => Math.min(99, currentQuantity + 1));
  };

  const handleQuantityInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const nextQuantity = Number(event.target.value);

    if (Number.isNaN(nextQuantity)) {
      return;
    }

    setQuantity(Math.min(99, Math.max(1, nextQuantity)));
  };

  const handleAddToCart = async () => {
    if (!productId || !product) {
      return;
    }

    void recordUserBehaviorEvent({
      event_name: "product_add_to_cart_clicked",
      user_id: user?.user_id ?? null,
      session_id: null,
      entity_type: "product",
      entity_id: product.product_id,
      properties: {
        page_path: window.location.pathname,
        product_id: product.product_id,
        product_name: product.product_name,
        source_page: "product_detail",
        quantity,
      },
    });

    if (!user) {
      setCartMessage(null);
      setCartErrorMessage("로그인 후 장바구니에 상품을 담을 수 있습니다.");
      return;
    }

    try {
      setIsAddingToCart(true);
      setCartMessage(null);
      setCartErrorMessage(null);

      let cartId = getStoredCartId();

      if (!cartId) {
        const createdCart = await createCart({
          user_id: user.user_id,
        });

        cartId = createdCart.cart_id;
        setStoredCartId(cartId);
      }

      try {
        await addCartItem(cartId, {
          product_id: product.product_id,
          quantity,
        });
      } catch {
        clearStoredPendingOrder(cartId);
        clearStoredCartId();

        const createdCart = await createCart({
          user_id: user.user_id,
        });

        cartId = createdCart.cart_id;
        setStoredCartId(cartId);

        await addCartItem(cartId, {
          product_id: product.product_id,
          quantity,
        });
      }

      clearStoredPendingOrder(cartId);
      setCartMessage("상품을 장바구니에 담았습니다.");
    } catch {
      setCartErrorMessage("상품 수량은 최대 99개까지만 담을 수 있습니다.");
    } finally {
      setIsAddingToCart(false);
    }
  };

  if (isLoading) {
    return <div className="state-box">상품 상세 정보를 불러오는 중입니다.</div>;
  }

  if (errorMessage || !product) {
    return (
      <section className="product-detail-page">
        <div className="state-box error">
          {errorMessage ?? "상품 정보를 확인할 수 없습니다."}
        </div>
        <Link to="/products" className="secondary-link">
          상품 목록으로 돌아가기
        </Link>
      </section>
    );
  }

  const hasDiscount = Number(product.list_price) !== Number(product.sale_price);

  return (
    <section className="product-detail-page">
      <Link to="/products" className="product-detail-back-link">
        ← 상품 목록으로 돌아가기
      </Link>

      <div className="product-detail-layout">
        <div className="product-detail-image">
          <span>{product.brand_name ?? "D2C"}</span>
        </div>

        <div className="product-detail-info">
          <div className="product-detail-meta">
            <span>{product.brand_name ?? "브랜드 미지정"}</span>
            <span>{product.product_status}</span>
          </div>

          <h1>{product.product_name}</h1>

          <div className="product-detail-price">
            <strong>{formatPrice(product.sale_price, product.currency)}</strong>
            {hasDiscount && (
              <span>{formatPrice(product.list_price, product.currency)}</span>
            )}
          </div>

          <div className="product-detail-description">
            <p>
              이 상품은 D2C Commerce Prototype의 상품 탐색 및 장바구니 흐름 검증을
              위한 샘플 상품입니다.
            </p>
          </div>

          <div className="quantity-control">
            <span>수량</span>
            <div className="quantity-stepper">
              <button type="button" onClick={handleDecreaseQuantity}>
                -
              </button>
              <input
                type="number"
                min="1"
                max="99"
                value={quantity}
                onChange={handleQuantityInputChange}
              />
              <button type="button" onClick={handleIncreaseQuantity}>
                +
              </button>
            </div>
          </div>

          {!user && (
            <div className="state-box product-detail-notice">
              로그인 후 장바구니에 상품을 담을 수 있습니다.
              <div className="product-detail-notice-actions">
                <Link to="/login" className="primary-link">
                  로그인
                </Link>
                <Link to="/signup" className="secondary-link">
                  회원가입
                </Link>
              </div>
            </div>
          )}

          {cartMessage && <div className="state-box success">{cartMessage}</div>}
          {cartErrorMessage && <div className="state-box error">{cartErrorMessage}</div>}

          <div className="product-detail-actions">
            <button
              type="button"
              className="primary-button"
              onClick={handleAddToCart}
              disabled={isAddingToCart || !product.is_active}
            >
              {isAddingToCart ? "장바구니 담는 중..." : "장바구니 담기"}
            </button>

            <Link to="/cart" className="secondary-link">
              장바구니 보기
            </Link>
          </div>
        </div>
      </div>

      <section className="product-review-section">
        <div className="product-review-header">
          <div>
            <p className="section-eyebrow">Reviews</p>
            <h2>상품 리뷰</h2>
            <p>구매자가 남긴 평점과 상세 후기를 확인해보세요.</p>
          </div>

          <div className="product-review-summary">
            <strong>
              {reviewSummary.averageRating
                ? Number(reviewSummary.averageRating).toFixed(1)
                : "-"}
            </strong>
            <span>리뷰 {reviewSummary.totalReviews}개</span>
          </div>
        </div>

        {reviewErrorMessage ? (
          <div className="state-box error">{reviewErrorMessage}</div>
        ) : reviews.length === 0 ? (
          <div className="state-box">아직 작성된 리뷰가 없습니다.</div>
        ) : (
          <div className="product-review-list">
            {reviews.map((review) => (
              <article key={review.review_id} className="product-review-card">
                <div className="product-review-card-header">
                  <div>
                    <strong>{review.review_title}</strong>
                    <p>
                      {formatReviewerName(review.user_name)} ·{" "}
                      {formatReviewDateTime(review.created_at)}
                    </p>
                  </div>

                  <div className="product-review-rating">
                    {"★".repeat(review.rating)}
                    {"☆".repeat(5 - review.rating)}
                  </div>
                </div>

                <p className="product-review-recommendation">
                  {getReviewRecommendationLabel(review.review_content)}
                </p>

                {getReviewDetailContent(review.review_content) && (
                  <p className="product-review-content">
                    {getReviewDetailContent(review.review_content)}
                  </p>
                )}
              </article>
            ))}
          </div>
        )}
      </section>
    </section>
  );
}