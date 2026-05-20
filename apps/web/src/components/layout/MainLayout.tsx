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
              <Link to="/coupons">쿠폰함</Link>
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

      <footer className="app-footer">
        <div className="app-footer-inner">
          <section className="app-footer-brand">
            <h2>D2C Commerce</h2>
            <p>
              상품 탐색부터 장바구니, 체크아웃, 주문, 결제 시뮬레이션, 리뷰 작성까지
              구매 흐름을 검증하는 D2C 커머스 프로토타입입니다.
            </p>
          </section>

          <nav className="app-footer-nav" aria-label="Footer navigation">
            <div>
              <h3>서비스</h3>
              <Link to="/products">상품 둘러보기</Link>
              <Link to="/cart">장바구니</Link>
              <Link to="/orders">주문 내역</Link>
              <Link to="/coupons">쿠폰함</Link>
            </div>

            <div>
              <h3>구매 흐름</h3>
              <span>상품 선택 및 장바구니 담기</span>
              <span>쿠폰 적용 및 주문 생성</span>
              <span>결제 성공·실패 시뮬레이션</span>
              <span>구매 상품 리뷰 작성</span>
            </div>

            <div>
              <h3>구현 범위</h3>
              <span>사용자 상태 기반 화면 제어</span>
              <span>주문·결제 상태 이력 관리</span>
              <span>상품별 리뷰 데이터 조회</span>
              <span>반응형 UI 및 공통 레이아웃</span>
            </div>
          </nav>
        </div>

        <div className="app-footer-bottom">
          <span>© 2026 jjunier. All rights reserved.</span>
          
          <a
            href="https://github.com/d2c-commerce-lab/prototype"
            target="_blank"
            rel="noreferrer"
            className="app-footer-repository-link"
            aria-label="GitHub Prototype Repository 새 창에서 열기"
          >
            <svg
              className="app-footer-github-icon"
              viewBox="0 0 24 24"
              aria-hidden="true"
              focusable="false"
            >
              <path
                fill="currentColor"
                d="M12 2C6.48 2 2 6.58 2 12.26c0 4.53 2.87 8.37 6.84 9.73.5.1.68-.22.68-.49 0-.24-.01-.88-.01-1.73-2.78.62-3.37-1.37-3.37-1.37-.45-1.18-1.11-1.49-1.11-1.49-.91-.64.07-.63.07-.63 1 .07 1.53 1.06 1.53 1.06.89 1.56 2.34 1.11 2.91.85.09-.66.35-1.11.63-1.37-2.22-.26-4.56-1.14-4.56-5.07 0-1.12.39-2.03 1.03-2.75-.1-.26-.45-1.3.1-2.71 0 0 .84-.28 2.75 1.05A9.28 9.28 0 0 1 12 6.99c.85 0 1.71.12 2.51.35 1.91-1.33 2.75-1.05 2.75-1.05.55 1.41.2 2.45.1 2.71.64.72 1.03 1.63 1.03 2.75 0 3.94-2.34 4.8-4.57 5.06.36.32.68.94.68 1.9 0 1.37-.01 2.48-.01 2.82 0 .27.18.59.69.49A10.1 10.1 0 0 0 22 12.26C22 6.58 17.52 2 12 2Z"
              />
            </svg>
            <span>GitHub Repository</span>
          </a>
        </div>
      </footer>
    </div>
  );
}