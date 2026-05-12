import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  getCart,
  removeCartItem,
  updateCartItemQuantity,
} from "../../services/cartApi";
import { getStoredCartId, getStoredUser } from "../../stores/userStore";
import type { CartDetail, CartItem } from "../../types/cart";

type CartItemWithTotals = CartItem & {
  line_amount?: string | number;
  line_total?: string | number;
};

const MIN_CART_QUANTITY = 0;
const MAX_CART_QUANTITY = 99;

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

function getCartItems(cart: CartDetail | null): CartItemWithTotals[] {
  if (!cart) {
    return [];
  }

  return (cart.cart_items ?? cart.items ?? []) as CartItemWithTotals[];
}

function getCartItemLineAmount(item: CartItemWithTotals) {
  const explicitLineAmount = item.line_total ?? item.line_amount;

  if (explicitLineAmount !== undefined) {
    return explicitLineAmount;
  }

  const calculatedAmount = Number(item.unit_price) * item.quantity;

  return Number.isNaN(calculatedAmount) ? undefined : calculatedAmount;
}

function getTotalQuantity(items: CartItemWithTotals[]) {
  return items.reduce((sum, item) => sum + item.quantity, 0);
}

function getFallbackTotalAmount(items: CartItemWithTotals[]) {
  return items.reduce((sum, item) => {
    const lineAmount = Number(getCartItemLineAmount(item));

    return Number.isNaN(lineAmount) ? sum : sum + lineAmount;
  }, 0);
}

function normalizeQuantity(value: number) {
  return Math.max(MIN_CART_QUANTITY, Math.min(MAX_CART_QUANTITY, value));
}

export function CartPage() {
  const storedUser = getStoredUser();
  const userId = storedUser?.user_id ?? null;
  const storedCartId = getStoredCartId();

  const [cart, setCart] = useState<CartDetail | null>(null);
  const [isLoading, setIsLoading] = useState(Boolean(userId && storedCartId));
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [actionErrorMessage, setActionErrorMessage] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [removingItemId, setRemovingItemId] = useState<string | null>(null);
  const [updatingItemId, setUpdatingItemId] = useState<string | null>(null);
  const [quantityDrafts, setQuantityDrafts] = useState<Record<string, string>>({});

  const cartItems = useMemo(() => getCartItems(cart), [cart]);
  const totalQuantity = useMemo(() => getTotalQuantity(cartItems), [cartItems]);
  const totalAmount = useMemo(
    () => cart?.total_amount ?? getFallbackTotalAmount(cartItems),
    [cart, cartItems],
  );
  const currency = cart?.currency ?? cartItems[0]?.currency ?? "KRW";

  const loadCart = useCallback(async () => {
    if (!userId || !storedCartId) {
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      setErrorMessage(null);

      const cartData = await getCart(storedCartId);
      setCart(cartData);
    } catch {
      setErrorMessage("장바구니 정보를 불러오지 못했습니다.");
    } finally {
      setIsLoading(false);
    }
  }, [storedCartId, userId]);

  useEffect(() => {
    loadCart();
  }, [loadCart]);

  useEffect(() => {
    const nextDrafts = cartItems.reduce<Record<string, string>>((drafts, item) => {
      drafts[item.cart_item_id] = String(item.quantity);
      return drafts;
    }, {});

    setQuantityDrafts(nextDrafts);
  }, [cartItems]);

  const handleRemoveItem = async (cartItemId: string) => {
    if (!storedCartId || removingItemId || updatingItemId) {
      return;
    }

    try {
      setRemovingItemId(cartItemId);
      setActionMessage(null);
      setErrorMessage(null);

      await removeCartItem(storedCartId, cartItemId);

      const refreshedCart = await getCart(storedCartId);
      setCart(refreshedCart);
    } catch {
      setErrorMessage("상품 제거에 실패했습니다. 잠시 후 다시 시도해주세요.");
    } finally {
      setRemovingItemId(null);
    }
  };

  const handleChangeQuantity = async (item: CartItem, nextQuantity: number) => {
    if (!storedCartId || updatingItemId) {
      return;
    }

    const normalizedQuantity = Math.max(0, Math.min(99, nextQuantity));

    try {
      setUpdatingItemId(item.cart_item_id);
      setActionMessage(null);
      setErrorMessage(null);

      if (normalizedQuantity === 0) {
        await removeCartItem(storedCartId, item.cart_item_id);
      } else {
        await updateCartItemQuantity(
          storedCartId,
          item.cart_item_id,
          normalizedQuantity,
        );
      }

      const refreshedCart = await getCart(storedCartId);
      setCart(refreshedCart);
    } catch {
      setActionErrorMessage("상품 수량 변경에 실패했습니다. 잠시 후 다시 시도해주세요.");
    } finally {
      setUpdatingItemId(null);
    }
  };

  const handleQuantityInputChange = (cartItemId: string, value: string) => {
    if (!/^\d*$/.test(value)) {
      return;
    }

    setQuantityDrafts((currentDrafts) => ({
      ...currentDrafts,
      [cartItemId]: value,
    }));
  };

  const handleQuantityInputBlur = (item: CartItemWithTotals) => {
    const draftValue = quantityDrafts[item.cart_item_id];

    if (draftValue === undefined || draftValue.trim() === "") {
      setQuantityDrafts((currentDrafts) => ({
        ...currentDrafts,
        [item.cart_item_id]: String(item.quantity),
      }));
      return;
    }

    const nextQuantity = Number(draftValue);

    if (Number.isNaN(nextQuantity)) {
      setQuantityDrafts((currentDrafts) => ({
        ...currentDrafts,
        [item.cart_item_id]: String(item.quantity),
      }));
      return;
    }

    handleChangeQuantity(item, nextQuantity);
  };

  if (!userId) {
    return (
      <section className="cart-page">
        <div className="cart-header">
          <p className="section-eyebrow">Shopping Cart</p>
          <h1>장바구니</h1>
          <p>로그인 후 장바구니에 담은 상품을 확인할 수 있습니다.</p>
        </div>

        <div className="state-box">
          장바구니를 확인하려면 로그인이 필요합니다.
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

  if (!storedCartId) {
    return (
      <section className="cart-page">
        <div className="cart-header">
          <p className="section-eyebrow">Shopping Cart</p>
          <h1>장바구니</h1>
          <p>아직 장바구니가 생성되지 않았습니다. 상품을 먼저 담아보세요.</p>
        </div>

        <div className="state-box">
          장바구니에 담긴 상품이 없습니다.
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
    <section className="cart-page">
      <div className="cart-header">
        <div>
          <p className="section-eyebrow">Shopping Cart</p>
          <h1>장바구니</h1>
          <p>장바구니에 담은 상품을 확인하고, 주문 단계로 이동할 수 있습니다.</p>
        </div>
      </div>

      {isLoading ? (
        <div className="state-box">장바구니 정보를 불러오는 중입니다.</div>
      ) : errorMessage ? (
        <div className="state-box error">{errorMessage}</div>
      ) : cartItems.length === 0 ? (
        <div className="state-box">
          {actionMessage ?? "장바구니에 담긴 상품이 없습니다."}
          <div className="cart-empty-actions">
            <Link to="/products" className="primary-link">
              상품 둘러보기
            </Link>
          </div>
        </div>
      ) : (
        <div className="cart-layout">
          <div className="cart-items">
            {actionMessage && <div className="state-box success">{actionMessage}</div>}
            {actionErrorMessage && <div className="state-box error">{actionErrorMessage}</div>}

            {cartItems.map((item) => {
              const lineAmount = getCartItemLineAmount(item);
              const isItemBusy =
                removingItemId === item.cart_item_id ||
                updatingItemId === item.cart_item_id;

              return (
                <article key={item.cart_item_id} className="cart-item-card">
                  <div className="cart-item-image">
                    <span>{item.brand_name ?? "D2C"}</span>
                  </div>

                  <div className="cart-item-info">
                    <div className="cart-item-meta">
                      <span>{item.brand_name || "브랜드 미지정"}</span>
                    </div>

                    <h2>{item.product_name ?? item.product_id}</h2>

                    <div className="cart-item-price">
                      <span>단가 {formatPrice(item.unit_price, item.currency)}</span>
                      <strong>{formatPrice(lineAmount, item.currency)}</strong>
                    </div>

                    <div className="cart-item-quantity-control">
                      <span>수량</span>

                      <div className="cart-quantity-stepper">
                        <button
                          type="button"
                          onClick={() => handleChangeQuantity(item, item.quantity - 1)}
                          disabled={isItemBusy}
                          aria-label={`${item.product_name ?? item.product_id} 수량 감소`}
                        >
                          -
                        </button>

                        <input
                          key={`${item.cart_item_id}-${item.quantity}`}
                          type="number"
                          min="1"
                          max="999"
                          defaultValue={item.quantity}
                          disabled={updatingItemId === item.cart_item_id}
                          onBlur={(event) => {
                            const nextQuantity = Number(event.target.value);

                            if (Number.isNaN(nextQuantity)) {
                              event.target.value = String(item.quantity);
                              return;
                            }

                            handleChangeQuantity(item, nextQuantity);
                          }}
                        />

                        <button
                          type="button"
                          onClick={() => handleChangeQuantity(item, item.quantity + 1)}
                          disabled={isItemBusy || item.quantity >= MAX_CART_QUANTITY}
                          aria-label={`${item.product_name ?? item.product_id} 수량 증가`}
                        >
                          +
                        </button>
                      </div>
                    </div>
                  </div>

                  <button
                    type="button"
                    className="cart-remove-button"
                    onClick={() => handleRemoveItem(item.cart_item_id)}
                    disabled={isItemBusy}
                  >
                    {removingItemId === item.cart_item_id ? "제거 중..." : "제거"}
                  </button>
                </article>
              );
            })}
          </div>

          <aside className="cart-summary-card">
            <h2>주문 요약</h2>

            <div className="cart-summary-row">
              <span>상품 종류</span>
              <strong>{cartItems.length}개</strong>
            </div>

            <div className="cart-summary-row">
              <span>총 수량</span>
              <strong>{totalQuantity}개</strong>
            </div>

            <div className="cart-summary-total">
              <span>총 결제 예정 금액</span>
              <strong>{formatPrice(totalAmount, currency)}</strong>
            </div>

            <Link to="/checkout" className="primary-link cart-checkout-link">
              주문 단계로 이동
            </Link>

            <Link to="/products" className="secondary-link cart-continue-link">
              계속 쇼핑하기
            </Link>
          </aside>
        </div>
      )}
    </section>
  );
}
