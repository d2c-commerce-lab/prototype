import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { ApiError } from "../../services/apiClient";
import { recordUserBehaviorEvent } from "../../services/eventLogApi";
import { createReview } from "../../services/reviewApi";
import { getStoredUser } from "../../stores/userStore";

const MIN_RATING = 1;
const MAX_RATING = 5;

type ProductRecommendation = "recommend" | "not_recommend";

function getValidId(value: string | null) {
  if (!value || value === "undefined" || value === "null") {
    return null;
  }

  return value;
}

export function ReviewCreatePage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const storedUser = getStoredUser();
  const userId = storedUser?.user_id ?? null;

  const productId = searchParams.get("product_id");
  const orderItemId = searchParams.get("order_item_id");
  const productName = searchParams.get("product_name") ?? "주문 상품";

  const validProductId = getValidId(productId);
  const validOrderItemId = getValidId(orderItemId);

  const [recommendation, setRecommendation] = 
  useState<ProductRecommendation | null>(null);
  const [rating, setRating] = useState(0);
  const [reviewTitle, setReviewTitle] = useState("");
  const [reviewContent, setReviewContent] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const isInvalidReviewTarget = !validProductId || !validOrderItemId;

  useEffect(() => {
    void recordUserBehaviorEvent({
      event_name: "review_create_page_viewed",
      user_id: userId,
      session_id: null,
      entity_type: validProductId ? "product" : null,
      entity_id: validProductId,
      properties: {
        page_path: window.location.pathname,
        product_id: validProductId,
        order_item_id: validOrderItemId,
        product_name: productName,
      },
    });
  }, [userId, validProductId, validOrderItemId, productName]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    void recordUserBehaviorEvent({
      event_name: "review_submit_clicked",
      user_id: userId,
      session_id: null,
      entity_type: validProductId ? "product" : null,
      entity_id: validProductId,
      properties: {
        page_path: window.location.pathname,
        product_id: validProductId,
        order_item_id: validOrderItemId,
        product_name: productName,
        rating,
        recommendation,
        has_review_title: Boolean(reviewTitle.trim()),
        has_review_content: Boolean(reviewContent.trim()),
      },
    });

    setErrorMessage(null);
    setSuccessMessage(null);

    if (!userId) {
      setErrorMessage("로그인 후 리뷰를 작성할 수 있습니다.");
      return;
    }

    if (!validProductId || !validOrderItemId) {
      setErrorMessage("리뷰를 작성할 주문 상품 정보를 확인할 수 없습니다.");
      return;
    }

    if (!recommendation) {
      setErrorMessage("상품 추천 여부를 선택해주세요.");
      return;
    }

    if (rating < MIN_RATING || rating > MAX_RATING) {
      setErrorMessage("평점을 선택해주세요.");
      return;
    }

    const normalizedTitle = reviewTitle.trim();
    const normalizedContent = reviewContent.trim();
    const recommendationLabel =
      recommendation === "recommend" ? "추천" : "비추천";

    const defaultReviewTitle =
      recommendation === "recommend"
        ? "만족스러운 구매 경험이었습니다."
        : "아쉬움이 남는 구매 경험이었습니다.";

    const defaultReviewContent = `상품 추천 여부: ${recommendationLabel}`;

    const finalReviewContent = normalizedContent
      ? `${defaultReviewContent}\n\n${normalizedContent}`
      : defaultReviewContent;

    try {
      setIsSubmitting(true);

      const reviewPayload = {
        user_id: userId,
        product_id: validProductId,
        order_item_id: validOrderItemId,
        rating,
        review_title: normalizedTitle || defaultReviewTitle,
        review_content: finalReviewContent,
      };

      const createdReview = await createReview(reviewPayload);

      setSuccessMessage("리뷰가 등록되었습니다.");

      navigate(`/products/${validProductId}`, {
        state: {
          createdReview,
        },
      });
    } catch (error) {
      if (
        error instanceof ApiError &&
        error.detail === "Review already exists for this order item"
      ) {
        setErrorMessage("이미 해당 주문 상품에 대한 리뷰를 작성했습니다.");
      } else if (
        error instanceof ApiError &&
        error.detail === "Review can only be created for purchased products"
      ) {
        setErrorMessage("구매 완료된 상품에 대해서만 리뷰를 작성할 수 있습니다.");
      } else if (error instanceof ApiError) {
        console.error("review create error detail", error.detail);

        setErrorMessage(
          typeof error.detail === "string"
            ? error.detail
            : JSON.stringify(error.detail, null, 2),
        );
      } else {
        setErrorMessage("리뷰 등록에 실패했습니다. 잠시 후 다시 시도해주세요.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!userId) {
    return (
      <section className="review-create-page">
        <div className="review-create-header">
          <p className="section-eyebrow">Review</p>
          <h1>리뷰 작성</h1>
          <p>로그인 후 구매한 상품에 대한 리뷰를 작성할 수 있습니다.</p>
        </div>

        <div className="state-box">
          리뷰를 작성하려면 로그인이 필요합니다.
          <div className="cart-empty-actions">
            <Link to="/login" className="primary-link">
              로그인
            </Link>
            <Link to="/orders" className="secondary-link">
              주문 내역으로 돌아가기
            </Link>
          </div>
        </div>
      </section>
    );
  }

  if (isInvalidReviewTarget) {
    return (
      <section className="review-create-page">
        <div className="review-create-header">
          <p className="section-eyebrow">Review</p>
          <h1>리뷰 작성</h1>
          <p>리뷰를 작성할 주문 상품 정보를 확인할 수 없습니다.</p>
        </div>

        <div className="state-box error">
          잘못된 접근입니다. 주문 내역에서 리뷰 작성 버튼을 통해 다시 시도해주세요.
          <div className="cart-empty-actions">
            <Link to="/orders" className="primary-link">
              주문 내역으로 돌아가기
            </Link>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="review-create-page">
      <div className="review-create-header">
        <p className="section-eyebrow">Review</p>
        <h1>리뷰 작성</h1>
        <p>구매한 상품에 대한 평점과 후기를 남겨주세요.</p>
      </div>

      <form className="review-form" onSubmit={handleSubmit}>
        <div className="review-target-box">
          <div className="review-target-info">
            <span>리뷰 작성 상품</span>
            <strong>{productName}</strong>
          </div>

          {validProductId && (
            <Link
            to={`/products/${validProductId}`}
            className="review-product-detail-link"
            >
              상품 상세 보기
            </Link>
          )}
        </div>

        {errorMessage && <div className="state-box error">{errorMessage}</div>}
        {successMessage && <div className="state-box success">{successMessage}</div>}

        <div className="review-form-section">
          <div className="review-form-label">
            <span>상품 추천 <small className="required-label">(필수 사항)</small></span>
            <small>이 상품을 전반적으로 추천하시나요?</small>
          </div>

          <div className="review-recommendation-group">
            <button
              type="button"
              className={
                recommendation === "recommend"
                  ? "review-recommendation-button active"
                  : "review-recommendation-button"
              }
              onClick={() => setRecommendation("recommend")}
              disabled={isSubmitting || Boolean(successMessage)}
            >
              추천
            </button>

            <button
              type="button"
              className={
                recommendation === "not_recommend"
                  ? "review-recommendation-button active danger"
                  : "review-recommendation-button danger"
              }
              onClick={() => setRecommendation("not_recommend")}
              disabled={isSubmitting || Boolean(successMessage)}
            >
              비추천
            </button>
          </div>
        </div>

        <div className="review-form-section">
          <div className="review-form-label">
            <span>평점 <small className="required-label">(필수 사항)</small></span>
            <small>별점을 선택해주세요.</small>
          </div>

          <div className="review-star-rating" aria-label="평점 선택">
            {[1, 2, 3, 4, 5].map((score) => (
              <button
                key={score}
                type="button"
                className={
                  score <= rating
                    ? "review-modify-star-btn active"
                    : "review-modify-star-btn"
                }
                onClick={() => setRating(score)}
                disabled={isSubmitting || Boolean(successMessage)}
                aria-label={`${score}점`}
              >
                ★
              </button>
            ))}
          </div>
        </div>

        <label className="form-field">
          <span>리뷰 제목 <small>(선택 사항)</small></span>
          <input
            type="text"
            value={reviewTitle}
            onChange={(event) => setReviewTitle(event.target.value)}
            placeholder="리뷰를 한 줄로 표현해 보세요."
            maxLength={100}
            disabled={isSubmitting || Boolean(successMessage)}
          />
        </label>

        <label className="form-field">
          <span>상세 리뷰 <small>(선택 사항)</small></span>
          <textarea
            value={reviewContent}
            onChange={(event) => setReviewContent(event.target.value)}
            placeholder="상품을 사용하며 느낀 점을 자유롭게 작성해 주세요."
            rows={8}
            maxLength={1000}
            disabled={isSubmitting || Boolean(successMessage)}
          />
        </label>

        <div className="review-form-actions">
          <Link to="/orders" className="secondary-link">
            주문 내역으로 돌아가기
          </Link>

          <button
            type="submit"
            className="primary-button"
            disabled={isSubmitting || Boolean(successMessage)}
          >
            {isSubmitting ? "등록 중" : "리뷰 등록"}
          </button>
        </div>
      </form>
    </section>
  );
}