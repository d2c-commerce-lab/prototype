---
title: Backend API Specification
version: v1.0
language: en
domain: backend
doc_type: api-specification
---

# Backend API Specification

## 0. Scope

This specification covers the following user flows.

- sign up
- login
- session start / end
- category retrieval
- product list retrieval
- product detail retrieval
- cart creation
- add item to cart
- remove cart item
- get cart detail
- enter checkout
- apply coupon
- create order
- simulate payment success / failure
- get order history
- create / update / delete review

## 1. Common Rules

### 1-1. Base URL

```text
http://localhost:8000
```

### 1-2. Content-Type

`POST`, `PATCH`, `DELETE` 요청 바디가 있는 경우 아래를 사용한다.

```http
Content-Type: application/json
```

### 1-3. Response Format

Successful responses use JSON objects by default, while failed responses use FastAPI’s standard `detail` structure.

Examples:

- sign up 중복: `409 Conflict` / `"Email already exists"`
- login 실패: `401 Unauthorized` / `"Invalid email or password"`

### 1-4. Standard Status Codes

- `200 OK`: successful read, update, or delete
- `201 Created`: successful creation
- `400 Bad Request`: invalid state or unmet input condition
- `401 Unauthorized`: authentication failure
- `403 Forbidden`: ownership or permission violation
- `404 Not Found`: target resource does not exist
- `409 Conflict`: duplicate creation attempt

---

## 2. Auth

### 2-1. sign up

#### Endpoint

```http
POST /auth/signup
```

#### Description

Creates a new user. Duplicate emails are rejected.

The service stores the following values in the `users` table.

- `email`
- `user_name`
- `password_hash`
- `signup_at`
- `user_status`
- `marketing_opt_in_yn`
- `created_at`
- `updated_at`

`password_hash`는 bcrypt 해시로 is stored.

#### Request Body

```json
{
  "email": "user@example.com",
  "user_name": "jun",
  "password": "Password123!",
  "marketing_opt_in_yn": true
}
```

#### Success Response

**Status**

```http
201 Created
```

**Response Body**

```json
{
  "user_id": "2693b094-42f7-4fde-be78-840330aeb6f9",
  "email": "user@example.com",
  "user_name": "jun",
  "user_status": "active",
  "marketing_opt_in_yn": true
}
```

#### Error Response

중복 이메일:

**Status**

```http
409 Conflict
```

**Response Body**

```json
{
  "detail": "Email already exists"
}
```

내부 stores 실패:

**Status**

```http
500 Internal Server Error
```

**Response Body**

```json
{
  "detail": "Failed to create user"
}
```

#### Notes

응답 필드와 에러 메시지는 현재 sign up 서비스 반환 구조와 일치한다.

---

### 2-2. login

#### Endpoint

```http
POST /auth/login
```

#### Description

Looks up a user by email and validates the password using bcrypt.

Queried fields:

- `user_id`
- `email`
- `user_name`
- `password_hash`
- `user_status`

authentication failure 시 이메일과 비밀번호를 구분하지 않고 동일 메시지를 반환한다.

#### Request Body

```json
{
  "email": "user@example.com",
  "password": "Password123!"
}
```

#### Success Response

**Status**

```http
200 OK
```

**Response Body**

```json
{
  "user_id": "2693b094-42f7-4fde-be78-840330aeb6f9",
  "email": "user@example.com",
  "user_name": "jun",
  "user_status": "active",
  "message": "Login successful"
}
```

#### Error Response

**Status**

```http
401 Unauthorized
```

**Response Body**

```json
{
  "detail": "Invalid email or password"
}
```

#### Notes

이 응답 구조와 메시지는 현재 login 서비스 반환값과 동일하다.

---

## 3. Session

### 3-1. Start Session

#### Endpoint

```http
POST /sessions
```

#### Description

Start Session 이벤트를 stores한다.

- `user_id`와 `campaign_id`are nullable
- `anonymous_id`, `platform`, `device_type`are required
- `session_start_at`, `created_at`are recorded with the current timestamp
- immediately after creation `session_end_at`은 `null`

#### Request Body

```json
{
  "user_id": "2693b094-42f7-4fde-be78-840330aeb6f9",
  "campaign_id": null,
  "anonymous_id": "anon-001",
  "platform": "web",
  "device_type": "desktop",
  "os_type": "windows",
  "browser_type": "chrome",
  "traffic_source": "google",
  "traffic_medium": "organic",
  "landing_page_url": "/products",
  "referrer_url": "https://www.google.com"
}
```

#### Success Response

**Status**

```http
201 Created
```

**Response Body**

```json
{
  "session_id": "6f0d8d87-7d14-41df-a2d3-6081cc56fb77",
  "user_id": "2693b094-42f7-4fde-be78-840330aeb6f9",
  "campaign_id": null,
  "anonymous_id": "anon-001",
  "session_start_at": "2026-05-03T10:00:00",
  "session_end_at": null,
  "platform": "web",
  "device_type": "desktop",
  "os_type": "windows",
  "browser_type": "chrome",
  "traffic_source": "google",
  "traffic_medium": "organic",
  "landing_page_url": "/products",
  "referrer_url": "https://www.google.com"
}
```

#### Error Response

**Status**

```http
500 Internal Server Error
```

**Response Body**

```json
{
  "detail": "Failed to create session"
}
```

#### Notes

The response fields and error messages match the current session creation service.

---

### 3-2. End Session

#### Endpoint

```http
PATCH /sessions/{session_id}/end
```

#### Description

Updates `session_end_at` to the current timestamp for an active session. The request fails if the session has already ended or does not exist.

#### Success Response

**Status**

```http
200 OK
```

**Response Body**

```json
{
  "session_id": "6f0d8d87-7d14-41df-a2d3-6081cc56fb77",
  "session_end_at": "2026-05-03T10:30:00",
  "message": "Session ended successfully"
}
```

#### Error Response

**Status**

```http
404 Not Found
```

**Response Body**

```json
{
  "detail": "Active session not found"
}
```

---

## 4. Catalog

### 4-1. Get Category List

#### Endpoint

```http
GET /categories
```

#### Description

Returns active categories only.

Returned columns:

- `category_id`
- `category_name`
- `category_depth`
- `category_status`

Sort order: category name ascending

#### Success Response

**Status**

```http
200 OK
```

**Response Body**

```json
[
  {
    "category_id": "11111111-1111-1111-1111-000000000001",
    "category_name": "Desk Setup",
    "category_depth": 1,
    "category_status": "active"
  }
]
```

---

### 4-2. product list retrieval

#### Endpoint

```http
GET /products
GET /products?category_id={category_id}
```

#### Description

Returns active products only, and allowed product states are limited to `on_sale` or `out_of_stock`.

Returned columns:

- `product_id`
- `category_id`
- `product_name`
- `product_status`
- `list_price`
- `sale_price`
- `currency`
- `brand_name`
- `is_active`

Sort order: product name ascending

#### Success Response

**Status**

```http
200 OK
```

**Response Body**

```json
[
  {
    "product_id": "33333333-3333-3333-3333-000000000001",
    "category_id": "11111111-1111-1111-1111-000000000001",
    "product_name": "Laptop Stand Lite",
    "product_status": "on_sale",
    "list_price": 29900,
    "sale_price": 24900,
    "currency": "KRW",
    "brand_name": "D2C Lab",
    "is_active": true
  }
]
```

---

### 4-3. product detail retrieval

#### Endpoint

```http
GET /products/{product_id}
```

#### Description

The endpoint is included in the draft, but the actual route/schema response contract has not yet been fixed in the current final version. Accordingly, this endpoint remains `TBD`.

#### Status

```text
TBD
```

#### Response Body

```text
TBD
```

---

## 5. Cart

### 5-1. cart creation 또는 활성 get cart detail

#### Endpoint

```http
POST /carts
```

#### Description

If the user already has an active cart, the API returns that cart. Otherwise, it creates a new cart.

The current implementation uses the same response shape for both newly created carts and reused active carts.

반환 필드:

- `cart_id`
- `user_id`
- `cart_status`
- `created_at`
- `updated_at`
- `checked_out_at`

#### Request Body

```json
{
  "user_id": "2693b094-42f7-4fde-be78-840330aeb6f9"
}
```

#### Success Response

**Status**

```http
200 OK
```

**Response Body**

```json
{
  "cart_id": "0c6b8b34-3d48-4fd0-8dc8-4fd1ff9f5e77",
  "user_id": "2693b094-42f7-4fde-be78-840330aeb6f9",
  "cart_status": "active",
  "created_at": "2026-05-03T11:00:00",
  "updated_at": "2026-05-03T11:00:00",
  "checked_out_at": null
}
```

#### Error Response

**Status**

```http
500 Internal Server Error
```

**Response Body**

```json
{
  "detail": "Failed to create cart"
}
```

---

### 5-2. add item to cart

#### Endpoint

```http
POST /carts/{cart_id}/items
```

#### Description

Verifies that the cart is in `active` state and that the product is active and in either `on_sale` or `out_of_stock` state before adding it.

Behavior:

- if the same product already exists, increase the quantity
- otherwise, insert a new row
- `unit_price`uses the product’s `sale_price`

#### Request Body

```json
{
  "product_id": "33333333-3333-3333-3333-000000000001",
  "quantity": 2
}
```

#### Success Response

**Status**

```http
200 OK
```

**Response Body**

```json
{
  "cart_item_id": "8cc5b9f1-8d0a-470f-b019-c4b5eb7a3d11",
  "cart_id": "0c6b8b34-3d48-4fd0-8dc8-4fd1ff9f5e77",
  "product_id": "33333333-3333-3333-3333-000000000001",
  "quantity": 2,
  "unit_price": 24900,
  "currency": "KRW",
  "added_at": "2026-05-03T11:05:00",
  "updated_at": "2026-05-03T11:05:00"
}
```

#### Error Response

장바구니 없음:

**Status**

```http
404 Not Found
```

**Response Body**

```json
{
  "detail": "Active cart not found"
}
```

상품 없음:

**Status**

```http
404 Not Found
```

**Response Body**

```json
{
  "detail": "Product not found"
}
```

수정 실패:

**Status**

```http
500 Internal Server Error
```

**Response Body**

```json
{
  "detail": "Failed to update cart item"
}
```

생성 실패:

**Status**

```http
500 Internal Server Error
```

**Response Body**

```json
{
  "detail": "Failed to add item to cart"
}
```

#### Notes

이 메시지와 성공 응답 구조는 현재 add item to cart 서비스와 일치한다.

---

### 5-3. Remove Cart Item

#### Endpoint

```http
DELETE /carts/{cart_id}/items/{cart_item_id}
```

#### Description

Verifies that the cart is active, then deletes the specified item.

#### Success Response

**Status**

```http
200 OK
```

**Response Body**

```json
{
  "cart_item_id": "8cc5b9f1-8d0a-470f-b019-c4b5eb7a3d11",
  "cart_id": "0c6b8b34-3d48-4fd0-8dc8-4fd1ff9f5e77",
  "message": "Cart item removed successfully"
}
```

#### Error Response

장바구니 없음:

**Status**

```http
404 Not Found
```

**Response Body**

```json
{
  "detail": "Active cart not found"
}
```

항목 없음:

**Status**

```http
404 Not Found
```

**Response Body**

```json
{
  "detail": "Cart item not found"
}
```

---

### 5-4. get cart detail

#### Endpoint

```http
GET /carts/{cart_id}
```

#### Description

Returns the active cart summary, item list, total quantity, and total amount.

The item list joins `cart_items` with `products` to include `product_name`, and `line_total` is calculated as `quantity * unit_price`.

#### Success Response

**Status**

```http
200 OK
```

**Response Body**

```json
{
  "cart_id": "0c6b8b34-3d48-4fd0-8dc8-4fd1ff9f5e77",
  "user_id": "2693b094-42f7-4fde-be78-840330aeb6f9",
  "cart_status": "active",
  "created_at": "2026-05-03T11:00:00",
  "updated_at": "2026-05-03T11:05:00",
  "checked_out_at": null,
  "total_items": 1,
  "total_quantity": 2,
  "total_amount": 49800,
  "currency": "KRW",
  "items": [
    {
      "cart_item_id": "8cc5b9f1-8d0a-470f-b019-c4b5eb7a3d11",
      "product_id": "33333333-3333-3333-3333-000000000001",
      "product_name": "Laptop Stand Lite",
      "quantity": 2,
      "unit_price": 24900,
      "currency": "KRW",
      "line_total": 49800,
      "added_at": "2026-05-03T11:05:00",
      "updated_at": "2026-05-03T11:05:00"
    }
  ]
}
```

#### Error Response

**Status**

```http
404 Not Found
```

**Response Body**

```json
{
  "detail": "Active cart not found"
}
```

---

## 6. Checkout / Coupon

### 6-1. enter checkout

#### Endpoint

```http
GET /checkout/{cart_id}
```

#### Description

Returns the active cart, cart items, user information, and available coupon list in a single response.

Coupon inclusion conditions:

- `coupon_status='active'`
- within the validity window
- current cart total is greater than or equal to `minimum_order_amount`

#### Success Response

**Status**

```http
200 OK
```

**Response Body**

```json
{
  "cart_id": "0c6b8b34-3d48-4fd0-8dc8-4fd1ff9f5e77",
  "user_id": "2693b094-42f7-4fde-be78-840330aeb6f9",
  "cart_status": "active",
  "total_items": 1,
  "total_quantity": 2,
  "total_amount": 49800,
  "currency": "KRW",
  "items": [],
  "user": {
    "user_id": "2693b094-42f7-4fde-be78-840330aeb6f9",
    "email": "user@example.com",
    "user_name": "jun",
    "user_status": "active",
    "marketing_opt_in_yn": true
  },
  "available_coupons": [
    {
      "coupon_id": "44444444-4444-4444-4444-000000000001",
      "campaign_id": null,
      "coupon_name": "WELCOME10",
      "coupon_type": "percentage",
      "discount_value": 10,
      "minimum_order_amount": 30000,
      "coupon_status": "active",
      "valid_start_at": "2026-05-01T00:00:00",
      "valid_end_at": "2026-05-31T23:59:59"
    }
  ]
}
```

#### Error Response

장바구니 없음:

**Status**

```http
404 Not Found
```

**Response Body**

```json
{
  "detail": "Active cart not found"
}
```

빈 장바구니:

**Status**

```http
400 Bad Request
```

**Response Body**

```json
{
  "detail": "Cart is empty"
}
```

---

### 6-2. apply coupon

#### Endpoint

```http
POST /carts/{cart_id}/apply-coupon
```

#### Description

장바구니 총액 기준으로 apply coupon 가능 여부를 판단하고 할인 결과를 반환한다.

Currently supported `coupon_type` values:

- `percentage`
- `fixed_amount`

#### Request Body

```json
{
  "coupon_name": "WELCOME10"
}
```

#### Success Response

**Status**

```http
200 OK
```

**Response Body**

```json
{
  "cart_id": "0c6b8b34-3d48-4fd0-8dc8-4fd1ff9f5e77",
  "coupon": {
    "coupon_id": "44444444-4444-4444-4444-000000000001",
    "campaign_id": null,
    "coupon_name": "WELCOME10",
    "coupon_type": "percentage",
    "discount_value": 10,
    "minimum_order_amount": 30000,
    "coupon_status": "active",
    "valid_start_at": "2026-05-01T00:00:00",
    "valid_end_at": "2026-05-31T23:59:59"
  },
  "total_amount": 49800,
  "discount_amount": 4980,
  "final_amount": 44820,
  "currency": "KRW",
  "message": "Coupon applied successfully"
}
```

#### Error Response

장바구니 없음:

**Status**

```http
404 Not Found
```

**Response Body**

```json
{
  "detail": "Active cart not found"
}
```

빈 장바구니:

**Status**

```http
400 Bad Request
```

**Response Body**

```json
{
  "detail": "Cart is empty"
}
```

쿠폰 없음:

**Status**

```http
404 Not Found
```

**Response Body**

```json
{
  "detail": "Coupon not found"
}
```

최소 주문금액 미달:

**Status**

```http
400 Bad Request
```

**Response Body**

```json
{
  "detail": "Cart total does not meet coupon minimum order amount"
}
```

미지원 쿠폰 타입:

**Status**

```http
400 Bad Request
```

**Response Body**

```json
{
  "detail": "Unsupported coupon type"
}
```

---

## 7. Order / Payment

### 7-1. create order

#### Endpoint

```http
POST /orders
```

#### Description

Converts an active cart into an order.

create order 시:

- `orders`에는 `user_id`, `cart_id`, `coupon_id`, `subtotal_amount`, `discount_amount`, `total_amount`, `currency` stores
- `order_items`에는 `discount_amount`, `final_item_amount`, `line_total`stores line-level pricing including
- the cart state is changed to `checked_out`

#### Request Body

```json
{
  "cart_id": "0c6b8b34-3d48-4fd0-8dc8-4fd1ff9f5e77",
  "coupon_name": "WELCOME10"
}
```

#### Success Response

**Status**

```http
201 Created
```

**Response Body**

```json
{
  "order_id": "7e5f56e2-c62d-4d18-9c3d-c4e56b1e1483",
  "user_id": "2693b094-42f7-4fde-be78-840330aeb6f9",
  "cart_id": "0c6b8b34-3d48-4fd0-8dc8-4fd1ff9f5e77",
  "order_status": "created",
  "subtotal_amount": 49800,
  "discount_amount": 4980,
  "total_amount": 44820,
  "currency": "KRW",
  "coupon_name": "WELCOME10",
  "ordered_at": "2026-05-03T11:20:00",
  "items": [
    {
      "order_item_id": "91d3b1f5-0a9e-45a0-8ae6-7780af6a7c2b",
      "product_id": "33333333-3333-3333-3333-000000000001",
      "product_name": "Laptop Stand Lite",
      "quantity": 2,
      "unit_price": 24900,
      "line_total": 49800,
      "currency": "KRW"
    }
  ],
  "message": "Order created successfully"
}
```

#### Error Response

활성 장바구니 없음:

**Status**

```http
404 Not Found
```

**Response Body**

```json
{
  "detail": "Active cart not found"
}
```

빈 장바구니:

**Status**

```http
400 Bad Request
```

**Response Body**

```json
{
  "detail": "Cart is empty"
}
```

쿠폰 없음:

**Status**

```http
404 Not Found
```

**Response Body**

```json
{
  "detail": "Coupon not found"
}
```

최소 주문금액 미달:

**Status**

```http
400 Bad Request
```

**Response Body**

```json
{
  "detail": "Cart total does not meet coupon minimum order amount"
}
```

미지원 쿠폰 타입:

**Status**

```http
400 Bad Request
```

**Response Body**

```json
{
  "detail": "Unsupported coupon type"
}
```

create order 실패:

**Status**

```http
500 Internal Server Error
```

**Response Body**

```json
{
  "detail": "Failed to create order"
}
```

주문 항목 생성 실패:

**Status**

```http
500 Internal Server Error
```

**Response Body**

```json
{
  "detail": "Failed to create order item"
}
```

---

### 7-2. simulate payment success / failure

#### Endpoint

```http
POST /payments/simulate
```

#### Description

Checks the current order state, then simulates a payment result.

Payable condition:

- order state must be `created` 또는 `payment_failed`

State transition:

- success → order becomes `paid`
- failure → order becomes `payment_failed`

`payments`에는 `paid_amount`, `pg_provider`, `transaction_id`, `failure_code` 등이 is stored.

#### Request Body

```json
{
  "order_id": "7e5f56e2-c62d-4d18-9c3d-c4e56b1e1483",
  "payment_method": "card",
  "simulate_result": "success"
}
```

#### Success Response

**Status**

```http
200 OK
```

**Response Body**

```json
{
  "payment_id": "f3fd9fb7-c8b8-4098-b65c-bc2290d456ef",
  "order_id": "7e5f56e2-c62d-4d18-9c3d-c4e56b1e1483",
  "payment_method": "card",
  "payment_status": "paid",
  "requested_amount": 44820,
  "approved_amount": 44820,
  "failed_reason": null,
  "paid_at": "2026-05-03T11:25:00",
  "created_at": "2026-05-03T11:25:00",
  "message": "Payment simulated successfully"
}
```

실패 예시:

**Status**

```http
200 OK
```

**Response Body**

```json
{
  "payment_status": "failed",
  "requested_amount": 44820,
  "approved_amount": 0,
  "failed_reason": "SIMULATED_FAILURE"
}
```

#### Error Response

주문 없음:

**Status**

```http
404 Not Found
```

**Response Body**

```json
{
  "detail": "Order not found"
}
```

결제 불가 상태:

**Status**

```http
400 Bad Request
```

**Response Body**

```json
{
  "detail": "Order is not payable"
}
```

결제 row 생성 실패:

**Status**

```http
500 Internal Server Error
```

**Response Body**

```json
{
  "detail": "Failed to create payment"
}
```

---

### 7-3. get order history

#### Endpoint

```http
GET /orders?user_id={user_id}
```

#### Description

Returns the user’s order list in reverse chronological order.

Behavior:

- latest payment status is fetched via subquery
- `order_items`are queried separately and included as the item list
- `coupon_id` is resolved by joining `coupons` through `coupon_id`

#### Success Response

**Status**

```http
200 OK
```

**Response Body**

```json
{
  "user_id": "2693b094-42f7-4fde-be78-840330aeb6f9",
  "total_orders": 1,
  "orders": [
    {
      "order_id": "7e5f56e2-c62d-4d18-9c3d-c4e56b1e1483",
      "cart_id": "0c6b8b34-3d48-4fd0-8dc8-4fd1ff9f5e77",
      "order_status": "paid",
      "payment_status": "paid",
      "subtotal_amount": 49800,
      "discount_amount": 4980,
      "total_amount": 44820,
      "currency": "KRW",
      "coupon_name": "WELCOME10",
      "ordered_at": "2026-05-03T11:20:00",
      "items": [
        {
          "order_item_id": "91d3b1f5-0a9e-45a0-8ae6-7780af6a7c2b",
          "product_id": "33333333-3333-3333-3333-000000000001",
          "product_name": "Laptop Stand Lite",
          "quantity": 2,
          "unit_price": 24900,
          "line_total": 49800,
          "currency": "KRW"
        }
      ]
    }
  ]
}
```

#### Error Response

**Status**

```http
404 Not Found
```

**Response Body**

```json
{
  "detail": "User not found"
}
```

---

## 8. Review

### 8-1. Create Review

#### Endpoint

```http
POST /reviews
```

#### Description

A review can only be created for a **purchased order item (`order_item_id`)**.

Validation order:

1. user exists
2. product exists / is active
3. purchase history exists
4. 동일 `order_item_id` no duplicate review already exists for the same `order_item_id`

`review_status` defaults to `visible`이다.

#### Request Body

```json
{
  "user_id": "2693b094-42f7-4fde-be78-840330aeb6f9",
  "product_id": "33333333-3333-3333-3333-000000000001",
  "order_item_id": "91d3b1f5-0a9e-45a0-8ae6-7780af6a7c2b",
  "rating": 5,
  "review_title": "Great product",
  "review_content": "The product quality is excellent."
}
```

#### Success Response

**Status**

```http
201 Created
```

**Response Body**

```json
{
  "review_id": "31f744e3-8d5e-4b3e-8f8e-b0bf5d2f4a12",
  "user_id": "2693b094-42f7-4fde-be78-840330aeb6f9",
  "product_id": "33333333-3333-3333-3333-000000000001",
  "order_item_id": "91d3b1f5-0a9e-45a0-8ae6-7780af6a7c2b",
  "rating": 5,
  "review_title": "Great product",
  "review_content": "The product quality is excellent.",
  "review_status": "visible",
  "created_at": "2026-05-03T11:40:00",
  "updated_at": "2026-05-03T11:40:00",
  "message": "Review created successfully"
}
```

#### Error Response

사용자 없음:

**Status**

```http
404 Not Found
```

**Response Body**

```json
{
  "detail": "User not found"
}
```

상품 없음:

**Status**

```http
404 Not Found
```

**Response Body**

```json
{
  "detail": "Product not found"
}
```

구매 이력 없음:

**Status**

```http
400 Bad Request
```

**Response Body**

```json
{
  "detail": "Review can only be created for purchased products"
}
```

중복 리뷰:

**Status**

```http
409 Conflict
```

**Response Body**

```json
{
  "detail": "Review already exists for this order item"
}
```

생성 실패:

**Status**

```http
500 Internal Server Error
```

**Response Body**

```json
{
  "detail": "Failed to create review"
}
```

---

### 8-2. Update Review

#### Endpoint

```http
PATCH /reviews/{review_id}
```

#### Description

Only the review author can update it. A review already in `deleted` state cannot be updated.

Updatable fields:

- `rating`
- `review_title`
- `review_content`

#### Request Body

```json
{
  "user_id": "2693b094-42f7-4fde-be78-840330aeb6f9",
  "rating": 4,
  "review_title": "Updated title",
  "review_content": "Updated content"
}
```

#### Success Response

**Status**

```http
200 OK
```

**Response Body**

```json
{
  "review_id": "31f744e3-8d5e-4b3e-8f8e-b0bf5d2f4a12",
  "user_id": "2693b094-42f7-4fde-be78-840330aeb6f9",
  "product_id": "33333333-3333-3333-3333-000000000001",
  "order_item_id": "91d3b1f5-0a9e-45a0-8ae6-7780af6a7c2b",
  "rating": 4,
  "review_title": "Updated title",
  "review_content": "Updated content",
  "review_status": "visible",
  "created_at": "2026-05-03T11:40:00",
  "updated_at": "2026-05-03T11:45:00",
  "message": "Review updated successfully"
}
```

#### Error Response

리뷰 없음:

**Status**

```http
404 Not Found
```

**Response Body**

```json
{
  "detail": "Review not found"
}
```

타인 Update Review 시도:

**Status**

```http
403 Forbidden
```

**Response Body**

```json
{
  "detail": "You can only update your own review"
}
```

삭제된 Update Review 시도:

**Status**

```http
400 Bad Request
```

**Response Body**

```json
{
  "detail": "Deleted review cannot be updated"
}
```

수정 실패:

**Status**

```http
500 Internal Server Error
```

**Response Body**

```json
{
  "detail": "Failed to update review"
}
```

---

### 8-3. Delete Review

#### Endpoint

```http
DELETE /reviews/{review_id}
```

#### Description

Reviews are soft deleted by setting `review_status='deleted'`, rather than being physically removed.

Constraints:

- only the review author can delete it
- an already deleted review cannot be deleted again
- the current implementation validates ownership through `user_id` in the request body

#### Request Body

```json
{
  "user_id": "2693b094-42f7-4fde-be78-840330aeb6f9"
}
```

#### Success Response

**Status**

```http
200 OK
```

**Response Body**

```json
{
  "review_id": "31f744e3-8d5e-4b3e-8f8e-b0bf5d2f4a12",
  "user_id": "2693b094-42f7-4fde-be78-840330aeb6f9",
  "review_status": "deleted",
  "updated_at": "2026-05-03T11:50:00",
  "message": "Review deleted successfully"
}
```

#### Error Response

리뷰 없음:

**Status**

```http
404 Not Found
```

**Response Body**

```json
{
  "detail": "Review not found"
}
```

타인 Delete Review 시도:

**Status**

```http
403 Forbidden
```

**Response Body**

```json
{
  "detail": "You can only delete your own review"
}
```

이미 삭제된 리뷰:

**Status**

```http
400 Bad Request
```

**Response Body**

```json
{
  "detail": "Review is already deleted"
}
```

삭제 실패:

**Status**

```http
500 Internal Server Error
```

**Response Body**

```json
{
  "detail": "Failed to delete review"
}
```

---

## 9. Standard State Values

현재 문서 기준 Standard State Values은 아래와 같다.

- `users.user_status`: `active`
- `products.product_status`: `on_sale`, `out_of_stock`
- `carts.cart_status`: `active`, `checked_out`
- `orders.order_status`: `created`, `paid`, `payment_failed`
- `coupons.coupon_status`: `active`
- `payments.payment_status`: `requested`, `paid`, `failed`
- `reviews.review_status`: `visible`, `deleted`

---

## 10. Notes

- `POST /carts`is documented as `200 OK` because the current implementation either creates a new cart or returns the existing active cart through the same endpoint.
- `GET /products/{product_id}`is included in the draft, but remains `TBD` in this final version because the actual route/schema response has not yet been frozen.
- `DELETE /reviews/{review_id}`uses soft delete, and ownership validation is currently performed through `user_id` in the request body.
