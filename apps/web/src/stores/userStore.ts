const USER_STORAGE_KEY = "d2c_user";
const CART_STORAGE_KEY = "d2c_cart_id";

export type StoredUser = {
  user_id: string;
  email: string;
  user_name: string;
  user_status: string;
};

export function getStoredUser(): StoredUser | null {
  const raw = localStorage.getItem(USER_STORAGE_KEY);

  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw) as StoredUser;
  } catch {
    localStorage.removeItem(USER_STORAGE_KEY);
    return null;
  }
}

export function setStoredUser(user: StoredUser) {
  localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
}

export function clearStoredUser() {
  localStorage.removeItem(USER_STORAGE_KEY);
  localStorage.removeItem(CART_STORAGE_KEY);
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