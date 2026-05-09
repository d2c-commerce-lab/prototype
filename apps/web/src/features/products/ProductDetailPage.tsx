import { useParams } from "react-router-dom";

export function ProductDetailPage() {
  const { productId } = useParams();

  return (
    <section className="page-section">
      <h1>상품 상세</h1>
      <p>D2C-34에서 상품 상세 조회와 장바구니 담기 흐름을 구현합니다.</p>
      <p>productId: {productId}</p>
    </section>
  );
}