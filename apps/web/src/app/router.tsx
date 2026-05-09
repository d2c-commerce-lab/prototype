import { createBrowserRouter } from "react-router-dom";
import { MainLayout } from "../components/layout/MainLayout";
import { HomePage } from "../features/home/HomePage";
import { ProductListPage } from "../features/products/ProductListPage";
import { ProductDetailPage } from "../features/products/ProductDetailPage";
import { SignupPage } from "../features/auth/SignupPage";
import { LoginPage } from "../features/auth/LoginPage";
import { CartPage } from "../features/cart/CartPage";
import { CheckoutPage } from "../features/checkout/CheckoutPage";
import { OrderHistoryPage } from "../features/orders/OrderHistoryPage";
import { ReviewCreatePage } from "../features/reviews/ReviewCreatePage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <MainLayout />,
    children: [
      {
        index: true,
        element: <HomePage />
      },
      {
        path: "products",
        element: <ProductListPage />
      },
      {
        path: "products/:productId",
        element: <ProductDetailPage />
      },
      {
        path: "signup",
        element: <SignupPage />
      },
      {
        path: "login",
        element: <LoginPage />
      },
      {
        path: "cart",
        element: <CartPage />
      },
      {
        path: "checkout",
        element: <CheckoutPage />
      },
      {
        path: "orders",
        element: <OrderHistoryPage />
      },
      {
        path: "reviews/new",
        element: <ReviewCreatePage />
      }
    ]
  }
]);