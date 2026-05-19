import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getUserCoupons } from "../../services/couponApi";
import { getStoredUser } from "../../stores/userStore";
import type { UsedCoupon, UserCoupon, UserCouponWalletResponse } from "../../types/coupon";

const KST_TIME_ZONE = "Asia/Seoul";

function formatPrice(value: string | number, currency = "KRW") {
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

function parseServerDateTime(value: string) {
  const hasTimezone = /([zZ]|[+-]\d{2}:\d{2})$/.test(value);

  if (hasTimezone) {
    return new Date(value);
  }

  const normalizedValue = value.replace(
    /\.(\d{3})\d+/,
    ".$1",
  );

  return new Date(normalizedValue);
}

function formatDateTime(value?: string | null) {
  if (!value) {
    return "-";
  }

  const date = parseServerDateTime(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("ko-KR", {
    timeZone: KST_TIME_ZONE,
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function formatDate(value?: string | null) {
  if (!value) {
    return "-";
  }

  const date = parseServerDateTime(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("ko-KR", {
    timeZone: KST_TIME_ZONE,
    dateStyle: "medium",
  }).format(date);
}

function formatCouponBenefit(coupon: UserCoupon) {
  if (coupon.coupon_type === "percentage") {
    return `${Number(coupon.discount_value).toLocaleString("ko-KR")}% 할인`;
  }

  if (coupon.coupon_type === "fixed_amount") {
    return `${formatPrice(coupon.discount_value)} 할인`;
  }

  return `${coupon.discount_value} 할인`;
}

function CouponCard({ coupon }: { coupon: UserCoupon }) {
  return (
    <article className="coupon-card">
      <div className="coupon-card-header">
        <div>
          <span className="coupon-badge">사용 가능</span>
          <h2>{coupon.coupon_name}</h2>
        </div>
        <strong>{formatCouponBenefit(coupon)}</strong>
      </div>

      <div className="coupon-card-meta">
        <span>최소 주문 금액 {formatPrice(coupon.minimum_order_amount)}</span>
        <span>
          유효기간 {formatDate(coupon.valid_start_at)} ~{" "}
          {formatDate(coupon.valid_end_at)}
        </span>
      </div>
    </article>
  );
}

function UsedCouponCard({ coupon }: { coupon: UsedCoupon }) {
  return (
    <article className="coupon-card used">
      <div className="coupon-card-header">
        <div>
          <span className="coupon-badge used">사용 완료</span>
          <h2>{coupon.coupon_name}</h2>
        </div>
        <strong>{formatCouponBenefit(coupon)}</strong>
      </div>

      <div className="coupon-card-meta">
        <span>사용 주문번호 : {coupon.used_order_id}</span>
        <span>사용 일시 : {formatDateTime(coupon.used_at)}</span>
        <span>최소 주문 금액 : {formatPrice(coupon.minimum_order_amount)}</span>
      </div>
    </article>
  );
}

export function CouponWalletPage() {
  const storedUser = getStoredUser();
  const userId = storedUser?.user_id ?? null;

  const [couponWallet, setCouponWallet] =
    useState<UserCouponWalletResponse | null>(null);
  const [isLoading, setIsLoading] = useState(Boolean(userId));
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    async function loadCoupons() {
      if (!userId) {
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setErrorMessage(null);

        const data = await getUserCoupons(userId);
        setCouponWallet(data);
      } catch {
        setErrorMessage("쿠폰함을 불러오지 못했습니다.");
      } finally {
        setIsLoading(false);
      }
    }

    loadCoupons();
  }, [userId]);

  if (!userId) {
    return (
      <section className="coupon-wallet-page">
        <div className="coupon-wallet-header">
          <p className="section-eyebrow">Coupons</p>
          <h1>쿠폰함</h1>
          <p>로그인 후 보유 쿠폰과 사용 이력을 확인할 수 있습니다.</p>
        </div>

        <div className="state-box">
          쿠폰함을 확인하려면 로그인이 필요합니다.
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

  return (
    <section className="coupon-wallet-page">
      <div className="coupon-wallet-header">
        <p className="section-eyebrow">Coupons</p>
        <h1>쿠폰함</h1>
        <p>
          사용 가능한 쿠폰과 결제 완료 주문에서 사용한 쿠폰 이력을 확인합니다.
        </p>
      </div>

      {isLoading ? (
        <div className="state-box">쿠폰함을 불러오는 중입니다.</div>
      ) : errorMessage ? (
        <div className="state-box error">{errorMessage}</div>
      ) : !couponWallet ? (
        <div className="state-box">쿠폰 정보를 확인할 수 없습니다.</div>
      ) : (
        <div className="coupon-wallet-layout">
          <section className="coupon-wallet-section">
            <div className="coupon-wallet-section-header">
              <h2>사용 가능한 쿠폰</h2>
              <span>{couponWallet.available_coupons.length}개</span>
            </div>

            {couponWallet.available_coupons.length === 0 ? (
              <div className="state-box">현재 사용 가능한 쿠폰이 없습니다.</div>
            ) : (
              <div className="coupon-card-list">
                {couponWallet.available_coupons.map((coupon) => (
                  <CouponCard key={coupon.coupon_id} coupon={coupon} />
                ))}
              </div>
            )}
          </section>

          <section className="coupon-wallet-section">
            <div className="coupon-wallet-section-header">
              <h2>사용 완료 쿠폰</h2>
              <span>{couponWallet.used_coupons.length}개</span>
            </div>

            {couponWallet.used_coupons.length === 0 ? (
              <div className="state-box">아직 사용한 쿠폰이 없습니다.</div>
            ) : (
              <div className="coupon-card-list">
                {couponWallet.used_coupons.map((coupon) => (
                  <UsedCouponCard
                    key={`${coupon.coupon_id}-${coupon.used_order_id}`}
                    coupon={coupon}
                  />
                ))}
              </div>
            )}
          </section>
        </div>
      )}
    </section>
  );
}