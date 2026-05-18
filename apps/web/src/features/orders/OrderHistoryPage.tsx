import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { getOrderHistory } from "../../services/orderApi";
import { getStoredUser } from "../../stores/userStore";
import type { OrderHistoryItem, OrderItem } from "../../types/order";

type PaymentStatusFilter = "all" | "paid" | "failed" | "unpaid";

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

const KST_TIME_ZONE = "Asia/Seoul";

function parseServerDateTime(value: string) {
  const normalizedValue = value.includes("T")
    ? value
    : value.replace(" ", "T");

  const hasTimezone = /([zZ]|[+-]\d{2}:\d{2})$/.test(normalizedValue);

  if (hasTimezone) {
    return new Date(normalizedValue);
  }

  return new Date(`${normalizedValue}+09:00`);
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

function getOrderDateValue(order: OrderHistoryItem) {
  return order.history_event_at ?? order.ordered_at ?? order.created_at ?? "";
}

function getKstDateParts(value: string) {
  const date = parseServerDateTime(value);

  if (Number.isNaN(date.getTime())) {
    return null;
  }

  const parts = new Intl.DateTimeFormat("ko-KR", {
    timeZone: KST_TIME_ZONE,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(date);

  const year = parts.find((part) => part.type === "year")?.value;
  const month = parts.find((part) => part.type === "month")?.value;
  const day = parts.find((part) => part.type === "day")?.value;

  if (!year || !month || !day) {
    return null;
  }

  return { year, month, day };
}

function getOrderDateKey(order: OrderHistoryItem) {
  const value = getOrderDateValue(order);

  if (!value) {
    return "unknown";
  }

  const dateParts = getKstDateParts(value);

  if (!dateParts) {
    return value.slice(0, 10) || "unknown";
  }

  return `${dateParts.year}-${dateParts.month}-${dateParts.day}`;
}

function getOrderDateLabel(order: OrderHistoryItem) {
  const value = getOrderDateValue(order);

  if (!value) {
    return "날짜 미지정";
  }

  const date = parseServerDateTime(value);

  if (Number.isNaN(date.getTime())) {
    return value.slice(0, 10) || "날짜 미지정";
  }

  return new Intl.DateTimeFormat("ko-KR", {
    timeZone: KST_TIME_ZONE,
    dateStyle: "long",
  }).format(date);
}

function getOrderStatusLabel(status: string) {
  const statusMap: Record<string, string> = {
    created: "주문 생성",
    paid: "주문 완료",
    payment_failed: "주문 실패",
    cancelled: "주문 취소",
  };

  return statusMap[status] ?? status;
}

function getPaymentStatusLabel(status?: string | null) {
  if (!status) {
    return "결제 전";
  }

  const statusMap: Record<string, string> = {
    paid: "결제 성공",
    failed: "결제 실패",
    pending: "결제 대기",
  };

  return statusMap[status] ?? status;
}

function matchesPaymentStatusFilter(
  order: OrderHistoryItem,
  filter: PaymentStatusFilter,
) {
  if (filter === "all") {
    return true;
  }

  if (filter === "paid") {
    return order.payment_status === "paid";
  }

  if (filter === "failed") {
    return order.payment_status === "failed";
  }

  return !order.payment_status;
}

function getStatusTone(status?: string | null) {
  if (status === "paid") {
    return "success";
  }

  if (status === "failed" || status === "payment_failed") {
    return "error";
  }

  return "neutral";
}

function getOrderItems(order: OrderHistoryItem): OrderItem[] {
  return order.items ?? [];
}

export function OrderHistoryPage() {
  const storedUser = getStoredUser();
  const userId = storedUser?.user_id ?? null;

  const [orders, setOrders] = useState<OrderHistoryItem[]>([]);
  const [totalOrders, setTotalOrders] = useState(0);
  const [paymentStatusFilter, setPaymentStatusFilter] = 
    useState<PaymentStatusFilter>("all");
  const [isLoading, setIsLoading] = useState(Boolean(userId));
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const filteredOrders = useMemo(() => {
    return orders.filter((order) =>
      matchesPaymentStatusFilter(order, paymentStatusFilter),
    );
  }, [orders, paymentStatusFilter]);

  const sortedOrders = useMemo(() => {
    return [...filteredOrders].sort((a, b) => {
      const aValue = a.history_event_at ?? a.ordered_at ?? a.created_at ?? "";
      const bValue = b.history_event_at ?? b.ordered_at ?? b.created_at ?? "";

      const aTime = aValue ? parseServerDateTime(aValue).getTime() : 0;
      const bTime = bValue ? parseServerDateTime(bValue).getTime() : 0;

      const timeDiff =
        (Number.isNaN(bTime) ? 0 : bTime) - (Number.isNaN(aTime) ? 0 : aTime);

      if (timeDiff !== 0) {
        return timeDiff;
      }

      return String(b.order_history_id ?? b.order_id).localeCompare(
        String(a.order_history_id ?? a.order_id),
      );
    });
  }, [filteredOrders]);

  const paymentStatusCounts = useMemo(() => {
    return orders.reduce(
      (acc, order) => {
        if (order.payment_status === "paid") {
          acc.paid += 1;
        } else if (order.payment_status === "failed") {
          acc.failed += 1;
        } else {
          acc.unpaid += 1;
        }

        return acc;
      },
      {
        paid: 0,
        failed: 0,
        unpaid: 0,
      },
    );
  }, [orders]);

  const groupedOrders = useMemo(() => {
    const groups = new Map<
      string,
      {
        dateLabel: string;
        orders: OrderHistoryItem[];
      }
    >();

    sortedOrders.forEach((order) => {
      const dateKey = getOrderDateKey(order);
      const existingGroup = groups.get(dateKey);

      if (existingGroup) {
        existingGroup.orders.push(order);
        return;
      }

      groups.set(dateKey, {
        dateLabel: getOrderDateLabel(order),
        orders: [order],
      });
    });

    return Array.from(groups.entries()).map(([dateKey, group]) => ({
      dateKey,
      ...group,
    }));
  }, [sortedOrders]);

  useEffect(() => {
    async function loadOrders() {
      if (!userId) {
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setErrorMessage(null);

        const orderHistory = await getOrderHistory(userId);

        setOrders(orderHistory.orders);
        setTotalOrders(orderHistory.total_orders);
      } catch {
        setErrorMessage("주문 내역을 불러오지 못했습니다.");
      } finally {
        setIsLoading(false);
      }
    }

    loadOrders();
  }, [userId]);

  if (!userId) {
    return (
      <section className="order-history-page">
        <div className="order-history-header">
          <p className="section-eyebrow">Orders</p>
          <h1>주문 내역</h1>
          <p>로그인 후 주문 및 결제 상태를 확인할 수 있습니다.</p>
        </div>

        <div className="state-box">
          주문 내역을 확인하려면 로그인이 필요합니다.
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
    <section className="order-history-page">
      <div className="order-history-header">
        <p className="section-eyebrow">Orders</p>
        <h1>주문 내역</h1>
        <p>생성된 주문과 결제 성공/실패 시뮬레이션 결과를 확인합니다.</p>
      </div>

      {isLoading ? (
        <div className="state-box">주문 내역을 불러오는 중입니다.</div>
      ) : errorMessage ? (
        <div className="state-box error">{errorMessage}</div>
      ) : orders.length === 0 ? (
        <div className="state-box">
          아직 주문 내역이 없습니다.
          <div className="cart-empty-actions">
            <Link to="/products" className="primary-link">
              상품 둘러보기
            </Link>
          </div>
        </div>
      ) : (
        <>
          <div className="order-history-toolbar">
            <div className="order-history-count">
              총 {totalOrders}건의 주문이 있습니다.
              {paymentStatusFilter === "all" ? (
                <span>
                  {" "}
                  결제 성공 {paymentStatusCounts.paid}건 · 결제 실패{" "}
                  {paymentStatusCounts.failed}건 · 결제 전 {paymentStatusCounts.unpaid}건입니다.
                </span>
              ) : (
                <span> 현재 조건에 맞는 주문은 {filteredOrders.length}건입니다.</span>
              )}
            </div>
          </div>

          {sortedOrders.length === 0 ? (
            <div className="state-box">
              선택한 결제 상태에 해당하는 주문이 없습니다.
            </div>
          ) : (
            <div className="order-history-groups">
              {groupedOrders.map((group) => (
                <section key={group.dateKey} className="order-history-date-group">
                  <div className="order-history-date-row">
                    <h2 className="order-history-date-heading">{group.dateLabel}</h2>

                    {group.dateKey === groupedOrders[0]?.dateKey && (
                      <label className="order-history-filter">
                        <span>결제 상태</span>
                        <select
                          value={paymentStatusFilter}
                          onChange={(event) =>
                            setPaymentStatusFilter(event.target.value as PaymentStatusFilter)
                          }
                        >
                          <option value="all">모두</option>
                          <option value="paid">결제 성공</option>
                          <option value="failed">결제 실패</option>
                          <option value="unpaid">결제 전</option>
                        </select>
                      </label>
                    )}
                  </div>

                  <div className="order-history-list">
                  {group.orders.map((order) => {
                    const orderItems = getOrderItems(order);
                    const orderStatusTone = getStatusTone(order.order_status);
                    const paymentStatusTone = getStatusTone(order.payment_status);

                    return (
                      <article
                        key={
                          order.order_history_id ??
                          `${order.order_id}-${order.payment_id ?? "created"}-${
                            order.payment_status ?? "unpaid"
                          }-${order.history_event_at ?? order.ordered_at ?? order.created_at ?? ""}`
                        }
                        className="order-history-card"
                      >
                        <div className="order-history-card-header">
                          <div>
                            <p className="order-history-date">
                              {formatDateTime(order.history_event_at ?? order.ordered_at ?? order.created_at)}
                            </p>
                            <h2>주문번호 {order.order_id}</h2>
                          </div>

                          <div className="order-status-group">
                            <span className={`status-badge ${orderStatusTone}`}>
                              주문: {getOrderStatusLabel(order.order_status)}
                            </span>
                            <span className={`status-badge ${paymentStatusTone}`}>
                              결제: {getPaymentStatusLabel(order.payment_status)}
                            </span>
                          </div>
                        </div>

                        <div className="order-history-summary-grid">
                          <div>
                            <span>상품 금액</span>
                            <strong>
                              {formatPrice(
                                order.subtotal_amount ?? order.total_amount,
                                order.currency,
                              )}
                            </strong>
                          </div>

                          <div>
                            <span>할인 금액</span>
                            <strong>-{formatPrice(order.discount_amount ?? 0, order.currency)}</strong>
                          </div>

                          <div>
                            <span>쿠폰</span>
                            <strong>{order.coupon_name ?? "미적용"}</strong>
                          </div>

                          <div>
                            <span>최종 결제 금액</span>
                            <strong>{formatPrice(order.total_amount, order.currency)}</strong>
                          </div>
                        </div>

                        <div className="order-history-items">
                          {orderItems.length === 0 ? (
                            <p className="order-history-empty-items">
                              주문 상품 상세가 없습니다.
                            </p>
                          ) : (
                            orderItems.map((item) => {
                              const canCreateReview =
                                order.order_status === "paid" && order.payment_status === "paid";

                              return (
                                <div key={item.order_item_id} className="order-history-item-row">
                                  <div>
                                    <h3>{item.product_name ?? item.product_id}</h3>
                                    <p>
                                      수량 {item.quantity}개 · 단가{" "}
                                      {formatPrice(item.unit_price, item.currency)}
                                    </p>
                                  </div>

                                  <div className="order-history-item-actions">
                                    <strong>
                                      {formatPrice(
                                        item.line_total ??
                                          item.final_item_amount ??
                                          Number(item.unit_price) * Number(item.quantity),
                                        item.currency,
                                      )}
                                    </strong>

                                    {canCreateReview && (
                                      <Link
                                        to={`/reviews/new?product_id=${item.product_id}&order_item_id=${item.order_item_id}&product_name=${encodeURIComponent(
                                          item.product_name ?? item.product_id,
                                        )}`}
                                        className="secondary-link compact"
                                      >
                                        리뷰 작성
                                      </Link>
                                    )}
                                  </div>
                                </div>
                              );
                            })
                          )}
                        </div>
                      </article>
                    );
                  })}
                </div>
              </section>
            ))}
          </div>
        )}
      </>
    )}
    </section>
  );
}