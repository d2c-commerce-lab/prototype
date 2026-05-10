import { Link } from "react-router-dom";
import { getStoredUser } from "../../stores/userStore";

export function HomePage() {
  const user = getStoredUser();

  return (
    <section className="home-page">
      <div className="home-hero">
        <div className="home-hero-content">
          <p className="home-eyebrow">D2C Commerce Prototype</p>
          <h1>상품 탐색부터 주문, 결제, 리뷰까지 이어지는 커머스 흐름을 검증합니다.</h1>
          <p className="home-description">
            D2C Commerce Prototype은 사용자가 상품을 탐색하고, 장바구니에 담고,
            체크아웃과 결제를 거쳐 리뷰를 작성하는 전체 사용자 흐름을 검증하기 위한
            웹 프로토타입입니다.
          </p>

          <div className="home-hero-actions">
            <Link to="/products" className="primary-link">
              상품 둘러보기
            </Link>
            <Link to="/cart" className="secondary-link">
              장바구니 확인
            </Link>
          </div>
        </div>
      </div>

      <div className="home-grid">
        <Link to="/products" className="home-card">
          <span className="home-card-label">01</span>
          <h2>상품 탐색</h2>
          <p>카테고리와 상품 목록을 확인하고, 관심 상품의 상세 정보를 조회합니다.</p>
        </Link>

        <Link to="/cart" className="home-card">
          <span className="home-card-label">02</span>
          <h2>장바구니</h2>
          <p>상품을 장바구니에 담고, 주문 전 상품 구성과 금액을 확인합니다.</p>
        </Link>

        <Link to="/checkout" className="home-card">
          <span className="home-card-label">03</span>
          <h2>체크아웃</h2>
          <p>쿠폰 적용, 주문 생성, 결제 시뮬레이션으로 이어지는 구매 흐름을 진행합니다.</p>
        </Link>

        <Link to="/orders" className="home-card">
          <span className="home-card-label">04</span>
          <h2>주문 내역</h2>
          <p>주문 상태와 결제 상태를 확인하고, 구매 상품 기반 리뷰 작성으로 이동합니다.</p>
        </Link>
      </div>

      <div className="home-account-panel">
        {user ? (
          <>
            <div>
              <h2>{user.user_name}님, 계속해서 구매 흐름을 확인해보세요.</h2>
              <p>주문 내역과 장바구니에서 이전에 진행하던 흐름을 이어갈 수 있습니다.</p>
            </div>
            <div className="home-actions">
              <Link to="/orders" className="primary-link">
                주문 내역 보기
              </Link>
              <Link to="/cart" className="secondary-link">
                장바구니 보기
              </Link>
            </div>
          </>
        ) : (
          <>
            <div>
              <h2>회원가입 또는 로그인 후 전체 구매 흐름을 검증할 수 있습니다.</h2>
              <p>
                로그인 이후 사용자 식별자를 기반으로 장바구니, 주문, 리뷰 흐름이 연결됩니다.
              </p>
            </div>
            <div className="home-panel-actions">
              <Link to="/login" className="primary-link">
                로그인
              </Link>
              <Link to="/signup" className="secondary-link">
                회원가입
              </Link>
            </div>
          </>
        )}
      </div>
    </section>
  );
}