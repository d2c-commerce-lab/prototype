import { type ChangeEvent, useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  applyCoupon,
  createOrder,
  enterCheckout,
  simulatePayment,
} from "../../services/checkoutApi";
import { 
  clearStoredCartId,
  getStoredCartId, 
  getStoredUser, 
} from "../../stores/userStore";
import type {
  CheckoutSummary,
  CouponApplyResponse,
  OrderCreateResponse,
  PaymentSimulationResponse,
} from "../../types/checkout";
import { ApiError } from "../../services/apiClient";

const PAYMENT_METHOD = "card";

function formatPrice(value: string | number | undefined, currency = "KRW") {
  if (value === undefined || value === null) {
    return "-";
  }

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

function getCheckoutItemLineAmount(item: CheckoutSummary["items"][number]) {
  const explicitLineAmount = item.line_total ?? item.line_amount;

  if (explicitLineAmount !== undefined) {
    return explicitLineAmount;
  }

  const calculatedAmount = Number(item.unit_price) * Number(item.quantity);

  return Number.isNaN(calculatedAmount) ? 0 : calculatedAmount;
}

function getCheckoutItemsTotalAmount(items: CheckoutSummary["items"]) {
  return items.reduce((sum, item) => {
    const lineAmount = Number(getCheckoutItemLineAmount(item));

    return Number.isNaN(lineAmount) ? sum : sum + lineAmount;
  }, 0);
}

function getAppliedCouponName(
  appliedCoupon: CouponApplyResponse | null,
  fallbackCouponCode: string,
) {
  return (
    appliedCoupon?.coupon?.coupon_name ??
    appliedCoupon?.coupon_name ??
    appliedCoupon?.coupon_code ??
    fallbackCouponCode
  );
}

export function CheckoutPage() {
  const navigate = useNavigate();

  const storedUser = getStoredUser();
  const userId = storedUser?.user_id ?? null;
  const [checkoutCartId, setCheckoutCartId] = useState<string | null>(() =>
    getStoredCartId(),
  );

  const [checkout, setCheckout] = useState<CheckoutSummary | null>(null);
  const [couponCode, setCouponCode] = useState("");
  const [appliedCoupon, setAppliedCoupon] = useState<CouponApplyResponse | null>(null);
  const [createdOrder, setCreatedOrder] = useState<OrderCreateResponse | null>(null);
  const [paymentResult, setPaymentResult] = useState<PaymentSimulationResponse | null>(
    null,
  );

  const [isLoading, setIsLoading] = useState(Boolean(userId && checkoutCartId));
  const [isApplyingCoupon, setIsApplyingCoupon] = useState(false);
  const [isCreatingOrder, setIsCreatingOrder] = useState(false);
  const [isPaying, setIsPaying] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [actionMessageType, setActionMessageType] = useState<"success" | "error">(
    "success",
  );

  const currency = checkout?.currency ?? appliedCoupon?.currency ?? "KRW";

  const originalAmount = useMemo(() => {
    return (
      appliedCoupon?.original_amount ??
      checkout?.original_amount ??
      checkout?.total_amount ??
      (checkout ? getCheckoutItemsTotalAmount(checkout.items) : 0)
    );
  }, [appliedCoupon, checkout]);

  const discountAmount = useMemo(() => {
    return appliedCoupon?.discount_amount ?? checkout?.discount_amount ?? 0;
  }, [appliedCoupon, checkout]);

  const finalAmount = useMemo(() => {
    const couponFinalAmount = appliedCoupon?.final_amount ?? checkout?.final_amount;

    if (couponFinalAmount !== undefined) {
      return couponFinalAmount;
    }

    return Number(originalAmount) - Number(discountAmount);
  }, [appliedCoupon, checkout, originalAmount, discountAmount]);

  useEffect(() => {
    async function loadCheckout() {
      if (!userId || !checkoutCartId) {
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setErrorMessage(null);

        const checkoutData = await enterCheckout(checkoutCartId);
        setCheckout(checkoutData);
      } catch {
        clearStoredCartId();
        setCheckout(null);
        setErrorMessage(
          "장바구니 정보를 찾을 수 없습니다. 상품을 다시 장바구니에 담아주세요.",
        );
      } finally {
        setIsLoading(false);
      }
    }

    loadCheckout();
  }, [checkoutCartId, userId]);

  const handleCouponCodeChange = (event: ChangeEvent<HTMLInputElement>) => {
    setCouponCode(event.target.value);
  };

  const handleApplyCoupon = async () => {
    const normalizedCouponCode = couponCode.trim();

    setActionMessage(null);
    setErrorMessage(null);

    if (!checkoutCartId || !normalizedCouponCode) {
      setErrorMessage("쿠폰 코드를 입력해주세요.");
      return;
    }

    const appliedCouponName = getAppliedCouponName(appliedCoupon, "");

    if (
      appliedCouponName &&
      appliedCouponName.toLowerCase() === normalizedCouponCode.toLowerCase()
    ) {
      setErrorMessage("이미 사용된 쿠폰입니다.");
      return;
    }

    try {
      setIsApplyingCoupon(true);

      const couponResult = await applyCoupon(checkoutCartId, normalizedCouponCode);

      setAppliedCoupon(couponResult);
      setCouponCode("");
      setActionMessageType("success");
      setActionMessage("쿠폰이 적용되었습니다.");
    } catch (error) {
      setActionMessage(null);

      if (
        error instanceof ApiError &&
        error.detail === "Coupon has already been used"
      ) {
        setErrorMessage("이미 사용된 쿠폰입니다.");
      } else {
        setErrorMessage("쿠폰 적용에 실패했습니다. 쿠폰 코드를 확인해주세요.");
      }
    } finally {
      setIsApplyingCoupon(false);
    }
  };

  const handleCreateOrder = async () => {
    if (!checkoutCartId) {
      setErrorMessage("장바구니 정보를 확인할 수 없습니다.");
      return;
    }

    try {
      setIsCreatingOrder(true);
      setErrorMessage(null);
      setActionMessage(null);
      setPaymentResult(null);

      const order = await createOrder({
        cart_id: checkoutCartId,
        coupon_name: getAppliedCouponName(appliedCoupon, "") || null,
      });

      setCreatedOrder(order);
      setActionMessageType("success");
      setActionMessage("주문이 생성되었습니다. 결제 시뮬레이션을 진행할 수 있습니다.");
    } catch (error) {
      setActionMessage(null);

      if (
        error instanceof ApiError &&
        error.detail === "Coupon has already been used"
      ) {
        setErrorMessage("이미 사용된 쿠폰입니다.");
      } else {
        setErrorMessage("주문 생성에 실패했습니다. 장바구니 상태를 확인해주세요.");
      }
    } finally {
      setIsCreatingOrder(false);
    }
  };

  const handleSimulatePayment = async (simulateResult: "success" | "failed") => {
    if (!createdOrder) {
      setErrorMessage("먼저 주문을 생성해주세요.");
      return;
    }

    try {
      setIsPaying(true);
      setErrorMessage(null);
      setActionMessage(null);

      const result = await simulatePayment({
        order_id: createdOrder.order_id,
        payment_method: PAYMENT_METHOD,
        simulate_result: simulateResult,
      });

      setPaymentResult(result);

      if (result.payment_status === "paid") {
        clearStoredCartId();
        setActionMessageType("success");
        setActionMessage("결제 성공 시뮬레이션이 완료되었습니다.");
      } else {
        setActionMessageType("error")
        setActionMessage("결제 실패 시뮬레이션이 완료되었습니다.");
      }
    } catch {
      setErrorMessage("결제 시뮬레이션에 실패했습니다.");
    } finally {
      setIsPaying(false);
    }
  };

  if (!userId) {
    return (
      <section className="checkout-page">
        <div className="checkout-header">
          <p className="section-eyebrow">Checkout</p>
          <h1>체크아웃</h1>
          <p>로그인 후 주문 단계를 진행할 수 있습니다.</p>
        </div>

        <div className="state-box">
          체크아웃을 진행하려면 로그인이 필요합니다.
          <div className="cart-empty-actions">
            <Link to="/login" className="primary-link">
              로그인
            </Link>
            <Link to="/signup" className="secondary-link">
              회원가입
            </Link>
          </div>
        </div>
      </section>
    );
  }

  if (!checkoutCartId) {
    return (
      <section className="checkout-page">
        <div className="checkout-header">
          <p className="section-eyebrow">Checkout</p>
          <h1>체크아웃</h1>
          <p>주문할 장바구니를 찾을 수 없습니다.</p>
        </div>

        <div className="state-box">
          장바구니에 상품을 먼저 담아주세요.
          <div className="cart-empty-actions">
            <Link to="/products" className="primary-link">
              상품 둘러보기
            </Link>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="checkout-page">
      <div className="checkout-header">
        <p className="section-eyebrow">Checkout</p>
        <h1>주문 및 결제 시뮬레이션</h1>
        <p>
          장바구니 상품을 확인하고, 쿠폰 적용 후 주문 생성과 결제 성공/실패 흐름을
          검증합니다.
        </p>
      </div>

      {isLoading ? (
        <div className="state-box">체크아웃 정보를 불러오는 중입니다.</div>
      ) : errorMessage && !checkout ? (
        <div className="state-box error">{errorMessage}</div>
      ) : !checkout || checkout.items.length === 0 ? (
        <div className="state-box">
          주문할 상품이 없습니다.
          <div className="cart-empty-actions">
            <Link to="/products" className="primary-link">
              상품 둘러보기
            </Link>
          </div>
        </div>
      ) : (
        <div className="checkout-layout">
          <div className="checkout-main">
            {actionMessage && (
              <div className={`state-box ${actionMessageType}`}>
                {actionMessage}
              </div>
            )}
            {errorMessage && <div className="state-box error">{errorMessage}</div>}

            <section className="checkout-section">
              <h2>주문 상품</h2>

              <div className="checkout-items">
                {checkout.items.map((item) => (
                  <article key={item.cart_item_id} className="checkout-item">
                    <div>
                      <span className="checkout-item-brand">
                        {item.brand_name || "브랜드 미지정"}
                      </span>
                      <h3>{item.product_name ?? item.product_id}</h3>
                      <p>
                        수량 {item.quantity}개 · 단가{" "}
                        {formatPrice(item.unit_price, item.currency)}
                      </p>
                    </div>

                    <strong>
                      {formatPrice(
                        item.line_total ??
                          item.line_amount ??
                          Number(item.unit_price) * Number(item.quantity),
                        item.currency,
                      )}
                    </strong>
                  </article>
                ))}
              </div>
            </section>

            <section className="checkout-section">
              <h2>쿠폰 적용</h2>

              <div className="coupon-row">
                <input
                  type="text"
                  value={couponCode}
                  placeholder="쿠폰 코드를 입력하세요"
                  onChange={handleCouponCodeChange}
                  disabled={Boolean(createdOrder)}
                />
                <button
                  type="button"
                  className="secondary-button"
                  onClick={handleApplyCoupon}
                  disabled={isApplyingCoupon || Boolean(createdOrder)}
                >
                  {isApplyingCoupon ? "적용 중..." : "쿠폰 적용"}
                </button>
              </div>

              {appliedCoupon && (
                <p className="coupon-applied-text">
                  적용된 쿠폰: {getAppliedCouponName(appliedCoupon, "확인 불가")}
                </p>
              )}
            </section>

            <section className="checkout-section">
              <h2>주문 생성 및 결제</h2>

              <div className="checkout-actions">
                <button
                  type="button"
                  className="primary-button"
                  onClick={handleCreateOrder}
                  disabled={isCreatingOrder || Boolean(createdOrder)}
                >
                  {isCreatingOrder ? "주문 생성 중..." : "주문 생성"}
                </button>

                <button
                  type="button"
                  className="success-button"
                  onClick={() => handleSimulatePayment("success")}
                  disabled={isPaying || !createdOrder || Boolean(paymentResult)}
                >
                  결제 성공 시뮬레이션
                </button>

                <button
                  type="button"
                  className="danger-button"
                  onClick={() => handleSimulatePayment("failed")}
                  disabled={isPaying || !createdOrder || Boolean(paymentResult)}
                >
                  결제 실패 시뮬레이션
                </button>
              </div>

              {createdOrder && (
                <div className="checkout-result-box">
                  <span>생성된 주문 ID</span>
                  <strong>{createdOrder.order_id}</strong>
                </div>
              )}

              {paymentResult && (
                <div className="checkout-result-box">
                  <span>결제 상태</span>
                  <strong>{paymentResult.payment_status}</strong>
                  <p>
                    {paymentResult.payment_status === "paid"
                      ? "결제가 성공 처리되었습니다."
                      : "결제가 실패 처리되었습니다."}
                  </p>
                </div>
              )}

              {paymentResult && (
                <button
                  type="button"
                  className="primary-button"
                  onClick={() => navigate("/orders")}
                >
                  주문 내역으로 이동
                </button>
              )}
            </section>
          </div>

          <aside className="checkout-summary-card">
            <h2>결제 요약</h2>

            <div className="checkout-summary-row">
              <span>상품 금액</span>
              <strong>{formatPrice(originalAmount, currency)}</strong>
            </div>

            <div className="checkout-summary-row">
              <span>쿠폰 할인</span>
              <strong>-{formatPrice(discountAmount, currency)}</strong>
            </div>

            <div className="checkout-summary-total">
              <span>최종 결제 금액</span>
              <strong>{formatPrice(finalAmount, currency)}</strong>
            </div>

            <Link to="/cart" className="secondary-link checkout-back-link">
              장바구니로 돌아가기
            </Link>
          </aside>
        </div>
      )}
    </section>
  );
}