import {
  type ChangeEvent,
  type MouseEvent,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { Link } from "react-router-dom";
import { addCartItem, createCart } from "../../services/cartApi";
import { getCategories, getProducts } from "../../services/catalogApi";
import {
  getStoredCartId,
  getStoredUser,
  setStoredCartId,
} from "../../stores/userStore";
import type { Category, Product } from "../../types/catalog";

const PAGE_SIZE_OPTIONS = [12, 24, 48] as const;
const DEFAULT_PAGE_SIZE = 24;
const QUICK_ADD_QUANTITY = 1;

function formatPrice(value: string | number, currency: string) {
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

function getVisibleProducts(products: Product[], currentPage: number, pageSize: number) {
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;

  return products.slice(startIndex, endIndex);
}

export function ProductListPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedCategoryId, setSelectedCategoryId] = useState<string>("");
  const [pageSize, setPageSize] = useState<number>(DEFAULT_PAGE_SIZE);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [cartFeedbackMessage, setCartFeedbackMessage] = useState<string | null>(null);
  const [cartErrorMessage, setCartErrorMessage] = useState<string | null>(null);
  const [addingProductId, setAddingProductId] = useState<string | null>(null);

  const productListTopRef = useRef<HTMLDivElement | null>(null);

  const scrollToProductListTop = useCallback(() => {
    requestAnimationFrame(() => {
      productListTopRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    });
  }, []);

  const selectedCategoryName = useMemo(() => {
    if (!selectedCategoryId) {
      return "전체 상품";
    }

    return (
      categories.find((category) => category.category_id === selectedCategoryId)
        ?.category_name ?? "선택한 카테고리"
    );
  }, [categories, selectedCategoryId]);

  const totalPages = Math.max(1, Math.ceil(products.length / pageSize));

  const paginatedProducts = useMemo(
    () => getVisibleProducts(products, currentPage, pageSize),
    [products, currentPage, pageSize],
  );

  const pageStartItem = products.length === 0 ? 0 : (currentPage - 1) * pageSize + 1;
  const pageEndItem = Math.min(currentPage * pageSize, products.length);

  useEffect(() => {
    async function loadCategories() {
      try {
        const categoryData = await getCategories();
        setCategories(categoryData);
      } catch {
        setErrorMessage("카테고리 목록을 불러오지 못했습니다. 잠시 후 다시 시도해주세요.");
      }
    }

    loadCategories();
  }, []);

  useEffect(() => {
    async function loadProducts() {
      try {
        setIsLoading(true);
        setErrorMessage(null);

        const productData = await getProducts(selectedCategoryId || undefined);

        setProducts(productData);
        setCurrentPage(1);
      } catch {
        setErrorMessage("상품 목록을 불러오지 못했습니다. 잠시 후 다시 시도해주세요.");
      } finally {
        setIsLoading(false);
      }
    }

    loadProducts();
  }, [selectedCategoryId]);

  const handleCategorySelect = (categoryId: string) => {
    setSelectedCategoryId(categoryId);
    setCartFeedbackMessage(null);
    setCartErrorMessage(null);
  };

  const handlePageSizeChange = (event: ChangeEvent<HTMLSelectElement>) => {
    setPageSize(Number(event.target.value));
    setCurrentPage(1);
    scrollToProductListTop();
  };

  const handlePreviousPage = () => {
    setCurrentPage((page) => Math.max(1, page - 1));
    scrollToProductListTop();
  };

  const handleNextPage = () => {
    setCurrentPage((page) => Math.min(totalPages, page + 1));
    scrollToProductListTop();
  };

  const handleQuickAddToCart = async (
    event: MouseEvent<HTMLButtonElement>,
    product: Product,
  ) => {
    event.preventDefault();
    event.stopPropagation();

    const user = getStoredUser();

    if (!user) {
      setCartFeedbackMessage(null);
      setCartErrorMessage("로그인 후 장바구니에 상품을 담을 수 있습니다.");
      return;
    }

    try {
      setAddingProductId(product.product_id);
      setCartFeedbackMessage(null);
      setCartErrorMessage(null);

      let cartId = getStoredCartId();

      if (!cartId) {
        const createdCart = await createCart({
          user_id: user.user_id,
        });

        cartId = createdCart.cart_id;
        setStoredCartId(cartId);
      }

      await addCartItem(cartId, {
        product_id: product.product_id,
        quantity: QUICK_ADD_QUANTITY,
      });

    } catch {
      setCartErrorMessage("장바구니 담기에 실패했습니다. 잠시 후 다시 시도해주세요.");
    } finally {
      setAddingProductId(null);
    }
  };

  return (
    <section className="product-list-page">
      <div className="product-list-header">
        <div>
          <p className="section-eyebrow">Product Catalog</p>
          <h1>카테고리별 상품을 탐색해보세요.</h1>
          <p>
            상품 목록에서 관심 상품을 선택하면 상세 화면으로 이동하거나 바로 장바구니에
            담아 구매 흐름을 이어갈 수 있습니다.
          </p>
        </div>
      </div>

      <div className="category-filter">
        <button
          type="button"
          className={!selectedCategoryId ? "category-chip active" : "category-chip"}
          onClick={() => handleCategorySelect("")}
        >
          전체
        </button>

        {categories.map((category) => (
          <button
            key={category.category_id}
            type="button"
            className={
              selectedCategoryId === category.category_id
                ? "category-chip active"
                : "category-chip"
            }
            onClick={() => handleCategorySelect(category.category_id)}
          >
            {category.category_name}
          </button>
        ))}
      </div>

      <div ref={productListTopRef} className="product-list-toolbar">
        <div className="product-list-summary">
          <div>
            <h2>{selectedCategoryName}</h2>
            <span>
              {products.length}개 상품
              {products.length > 0 && ` · ${pageStartItem}-${pageEndItem}개 표시 중`}
            </span>
          </div>
        </div>

        <label className="page-size-control">
          <span>표시 개수</span>
          <select value={pageSize} onChange={handlePageSizeChange}>
            {PAGE_SIZE_OPTIONS.map((option) => (
              <option key={option} value={option}>
                {option}개씩 보기
              </option>
            ))}
          </select>
        </label>
      </div>

      {(cartFeedbackMessage || cartErrorMessage) && (
        <div className="product-list-feedback" aria-live="polite">
          {cartFeedbackMessage && <div className="state-box success">{cartFeedbackMessage}</div>}
          {cartErrorMessage && <div className="state-box error">{cartErrorMessage}</div>}
        </div>
      )}

      {isLoading ? (
        <div className="state-box">상품 목록을 불러오는 중입니다.</div>
      ) : errorMessage ? (
        <div className="state-box error">{errorMessage}</div>
      ) : products.length === 0 ? (
        <div className="state-box">표시할 상품이 없습니다.</div>
      ) : (
        <>
          <div className="product-grid">
            {paginatedProducts.map((product) => {
              const isAddingCurrentProduct = addingProductId === product.product_id;
              const isDiscounted = Number(product.list_price) !== Number(product.sale_price);

              return (
                <Link
                  key={product.product_id}
                  to={`/products/${product.product_id}`}
                  className="product-card"
                >
                  <div className="product-image-placeholder">
                    <span>{product.brand_name ?? "D2C"}</span>
                  </div>

                  <div className="product-card-body">
                    <div className="product-meta">
                      <span>{product.brand_name || "브랜드 미지정"}</span>
                      <span>{product.product_status}</span>
                    </div>

                    <h3>{product.product_name}</h3>

                    <div className="product-card-footer">
                      <div className="product-price-row">
                        <strong>{formatPrice(product.sale_price, product.currency)}</strong>
                        {isDiscounted && (
                          <span>{formatPrice(product.list_price, product.currency)}</span>
                        )}
                      </div>

                      <button
                        type="button"
                        className="product-card-cart-button"
                        onClick={(event) => handleQuickAddToCart(event, product)}
                        disabled={isAddingCurrentProduct || !product.is_active}
                        aria-label={`${product.product_name} 장바구니 담기`}
                      >
                        {isAddingCurrentProduct ? "담는 중" : "담기"}
                      </button>
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>

          <div className="pagination">
            <button
              type="button"
              onClick={handlePreviousPage}
              disabled={currentPage === 1}
            >
              이전
            </button>

            <span>
              {currentPage} / {totalPages}
            </span>

            <button
              type="button"
              onClick={handleNextPage}
              disabled={currentPage === totalPages}
            >
              다음
            </button>
          </div>
        </>
      )}
    </section>
  );
}
