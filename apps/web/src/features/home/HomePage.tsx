import { Link } from "react-router-dom";

export function HomePage() {
  return (
    <section className="page-section">
      <h1>D2C Commerce Prototype</h1>
      <p>상품 탐색부터 주문, 결제, 리뷰 작성까지 이어지는 D2C 커머스 프로토타입입니다.</p>

      <div className="action-row">
        <Link to="/products" className="primary-link">
          상품 보러가기
        </Link>
        <Link to="/orders" className="secondary-link">
          주문 내역 확인
        </Link>
      </div>
    </section>
  );
}