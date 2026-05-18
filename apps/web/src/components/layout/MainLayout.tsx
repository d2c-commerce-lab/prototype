import { useEffect, useState } from "react";
import { Link, Outlet } from "react-router-dom";
import {
  clearStoredUser,
  getStoredUser,
  USER_STORAGE_EVENT,
} from "../../stores/userStore";
import type { AuthUser } from "../../types/auth";

export function MainLayout() {
  const [user, setUser] = useState<AuthUser | null>(() => getStoredUser());

  useEffect(() => {
    const syncUser = () => {
      setUser(getStoredUser());
    };

    window.addEventListener(USER_STORAGE_EVENT, syncUser);
    window.addEventListener("storage", syncUser);

    return () => {
      window.removeEventListener(USER_STORAGE_EVENT, syncUser);
      window.removeEventListener("storage", syncUser);
    };
  }, []);

  const handleLogout = () => {
    clearStoredUser();
    window.location.href = "/";
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <Link to="/" className="app-logo">
          D2C Commerce
        </Link>

        <nav className="app-nav" aria-label="주요 메뉴">
          <Link to="/products">상품 둘러보기</Link>
          <Link to="/cart">장바구니</Link>

          {user ? (
            <>
              <Link to="/orders">주문 내역</Link>
              <span className="app-user">{user.user_name}님</span>
              <button type="button" onClick={handleLogout} className="link-button">
                로그아웃
              </button>
            </>
          ) : (
            <>
              <Link to="/login">로그인</Link>
              <Link to="/signup" className="signup-link">
                회원가입
              </Link>
            </>
          )}
        </nav>
      </header>

      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}