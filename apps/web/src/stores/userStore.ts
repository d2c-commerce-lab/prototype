import type { AuthUser } from "../types/auth";

const USER_STORAGE_KEY = "d2c_user";
const CART_STORAGE_KEY = "d2c_cart_id";
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
  notifyUserChanged();
}

export function getStoredCartId(): string | null {
  return localStorage.getItem(CART_STORAGE_KEY);
}

export function setStoredCartId(cartId: string) {
  localStorage.setItem(CART_STORAGE_KEY, cartId);
}

export function clearStoredCartId() {
  localStorage.removeItem(CART_STORAGE_KEY);
}