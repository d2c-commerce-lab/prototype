import type { AuthUser } from "../types/auth";

const USER_STORAGE_KEY = "d2c_user";
const CART_STORAGE_KEY = "d2c_cart_id";
const PENDING_ORDER_STORAGE_KEY = "d2c_pending_order_by_cart";
export const USER_STORAGE_EVENT = "d2c_user_changed";

function notifyUserChanged() {
  window.dispatchEvent(new Event(USER_STORAGE_EVENT));
}

export function getStoredUser(): AuthUser | null {
  const raw = localStorage.getItem(USER_STORAGE_KEY);

  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw) as AuthUser;
  } catch {
    localStorage.removeItem(USER_STORAGE_KEY);
    return null;
  }
}

export function setStoredUser(user: AuthUser) {
  localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
  notifyUserChanged();
}

export function clearStoredUser() {
  localStorage.removeItem(USER_STORAGE_KEY);
  localStorage.removeItem(CART_STORAGE_KEY);
  localStorage.removeItem(PENDING_ORDER_STORAGE_KEY);
  notifyUserChanged();
}

export type StoredPendingOrder = {
  order_id: string;
  cart_id: string;
  order_status: string;
  subtotal_amount?: string | number;
  discount_amount?: string | number;
  total_amount: string | number;
  currency: string;
  ordered_at?: string;
};

export function getStoredCartId(): string | null {
  return localStorage.getItem(CART_STORAGE_KEY);
}

export function setStoredCartId(cartId: string) {
  localStorage.setItem(CART_STORAGE_KEY, cartId);
}

export function clearStoredCartId() {
  localStorage.removeItem(CART_STORAGE_KEY);
}

function getPendingOrderMap() {
  const rawValue = localStorage.getItem(PENDING_ORDER_STORAGE_KEY);

  if (!rawValue) {
    return {};
  }

  try {
    return JSON.parse(rawValue) as Record<string, StoredPendingOrder>;
  } catch {
    localStorage.removeItem(PENDING_ORDER_STORAGE_KEY);
    return {};
  }
}

export function getStoredPendingOrder(cartId: string) {
  const pendingOrderMap = getPendingOrderMap();

  return pendingOrderMap[cartId] ?? null;
}

export function setStoredPendingOrder(order: StoredPendingOrder) {
  const pendingOrderMap = getPendingOrderMap();

  pendingOrderMap[order.cart_id] = order;

  localStorage.setItem(
    PENDING_ORDER_STORAGE_KEY,
    JSON.stringify(pendingOrderMap),
  );
}

export function clearStoredPendingOrder(cartId: string) {
  const pendingOrderMap = getPendingOrderMap();

  delete pendingOrderMap[cartId];

  localStorage.setItem(
    PENDING_ORDER_STORAGE_KEY,
    JSON.stringify(pendingOrderMap),
  );
}