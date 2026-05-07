---
title: 백엔드 API 명세서
version: v1.0
language: ko
domain: backend
doc_type: api-specification
---

# 백엔드 API 명세서

## 0. 문서 범위

본 명세서는 아래 사용자 흐름을 기준으로 정리한다.

- 회원가입
- 로그인
- 세션 시작/종료
- 카테고리 조회
- 상품 목록 조회
- 상품 상세 조회
- 장바구니 생성
- 장바구니 담기
- 장바구니 제거
- 장바구니 조회
- 체크아웃 진입
- 쿠폰 적용
- 주문 생성
- 결제 성공/실패 시뮬레이션
- 주문 내역 조회
- 리뷰 생성/수정/삭제

## 1. 공통 규칙

### 1-1. Base URL

```text
http://localhost:8000
```

### 1-2. Content-Type

`POST`, `PATCH`, `DELETE` 요청 바디가 있는 경우 아래를 사용한다.

```http
Content-Type: application/json
```

### 1-3. 응답 형식

성공 응답은 JSON 객체를 기본으로 하며, 실패 응답은 FastAPI 기본 `detail` 구조를 사용한다.

예를 들어:

- 회원가입 중복: `409 Conflict` / `"Email already exists"`
- 로그인 실패: `401 Unauthorized` / `"Invalid email or password"`

### 1-4. 주요 상태 코드 규칙

- `200 OK`: 조회, 수정, 삭제 성공
- `201 Created`: 생성 성공
- `400 Bad Request`: 상태나 입력 조건이 맞지 않음
- `401 Unauthorized`: 인증 실패
- `403 Forbidden`: 타인 리소스 수정/삭제 시도
- `404 Not Found`: 대상 리소스 없음
- `409 Conflict`: 중복 생성 시도

---

## 2. 인증(Auth)

### 2-1. 회원가입

#### Endpoint

```http
POST /auth/signup
```

#### 설명

신규 사용자를 생성한다. 이메일 중복이 있으면 생성하지 않는다.

서비스는 `users` 테이블에 아래 값을 저장한다.

- `email`
- `user_name`
- `password_hash`
- `signup_at`
- `user_status`
- `marketing_opt_in_yn`
- `created_at`
- `updated_at`

`password_hash`는 bcrypt 해시로 저장된다.

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

내부 저장 실패:

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

#### 비고

응답 필드와 에러 메시지는 현재 회원가입 서비스 반환 구조와 일치한다.

---

### 2-2. 로그인

#### Endpoint

```http
POST /auth/login
```

#### 설명

이메일로 사용자를 조회하고 bcrypt로 비밀번호를 검증한다.

조회 대상은 아래와 같다.

- `user_id`
- `email`
- `user_name`
- `password_hash`
- `user_status`

인증 실패 시 이메일과 비밀번호를 구분하지 않고 동일 메시지를 반환한다.

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

#### 비고

이 응답 구조와 메시지는 현재 로그인 서비스 반환값과 동일하다.

---

## 3. 세션(Session)

### 3-1. 세션 시작

#### Endpoint

```http
POST /sessions
```

#### 설명

세션 시작 이벤트를 저장한다.

- `user_id`와 `campaign_id`는 nullable
- `anonymous_id`, `platform`, `device_type`는 필수
- `session_start_at`, `created_at`은 현재 시각으로 기록
- 생성 직후 `session_end_at`은 `null`

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

#### 비고

응답 필드와 에러 메시지는 현재 세션 생성 서비스와 일치한다.

---

### 3-2. 세션 종료

#### Endpoint

```http
PATCH /sessions/{session_id}/end
```

#### 설명

활성 세션의 `session_end_at`을 현재 시각으로 업데이트한다. 이미 종료된 세션이거나 존재하지 않는 세션이면 실패한다.

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

## 4. 카탈로그(Catalog)

### 4-1. 카테고리 목록 조회

#### Endpoint

```http
GET /categories
```

#### 설명

활성 상태 카테고리만 조회한다.

반환 컬럼:

- `category_id`
- `category_name`
- `category_depth`
- `category_status`

정렬 기준: 카테고리명 오름차순

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

### 4-2. 상품 목록 조회

#### Endpoint

```http
GET /products
GET /products?category_id={category_id}
```

#### 설명

활성 상품만 조회하며, 상품 상태는 `on_sale` 또는 `out_of_stock`만 허용한다.

반환 컬럼:

- `product_id`
- `category_id`
- `product_name`
- `product_status`
- `list_price`
- `sale_price`
- `currency`
- `brand_name`
- `is_active`

정렬 기준: 상품명 오름차순

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

### 4-3. 상품 상세 조회

#### Endpoint

```http
GET /products/{product_id}
```

#### 설명

현재 초안에는 엔드포인트가 포함돼 있으나, 이번 최종본 기준으로는 **실제 route/schema 응답 구조를 별도 고정하지 못한 상태**다. 따라서 이 엔드포인트는 `TBD`로 유지한다.

#### Status

```text
TBD
```

#### Response Body

```text
TBD
```

---

## 5. 장바구니(Cart)

### 5-1. 장바구니 생성 또는 활성 장바구니 조회

#### Endpoint

```http
POST /carts
```

#### 설명

사용자에게 활성 장바구니가 이미 있으면 그 장바구니를 반환하고, 없으면 새 장바구니를 생성한다.

현재 구현은 신규 생성과 기존 활성 장바구니 반환을 같은 응답 구조로 처리한다.

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

### 5-2. 장바구니 담기

#### Endpoint

```http
POST /carts/{cart_id}/items
```

#### 설명

장바구니가 `active` 상태인지 확인하고, 상품이 활성 상품이며 상태가 `on_sale` 또는 `out_of_stock`인지 확인한 뒤 담는다.

동작 방식:

- 같은 상품이 이미 있으면 수량 증가
- 없으면 새 row 추가
- `unit_price`는 상품의 `sale_price` 사용

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

#### 비고

이 메시지와 성공 응답 구조는 현재 장바구니 담기 서비스와 일치한다.

---

### 5-3. 장바구니 항목 제거

#### Endpoint

```http
DELETE /carts/{cart_id}/items/{cart_item_id}
```

#### 설명

활성 장바구니인지 확인한 뒤 해당 항목을 삭제한다.

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

### 5-4. 장바구니 조회

#### Endpoint

```http
GET /carts/{cart_id}
```

#### 설명

활성 장바구니 기본 정보와 항목 목록, 총 수량, 총 금액을 반환한다.

항목 목록은 `cart_items`와 `products`를 조인해 `product_name`을 포함하고, `line_total`은 `quantity * unit_price` 계산값이다.

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

## 6. 체크아웃 / 쿠폰

### 6-1. 체크아웃 진입

#### Endpoint

```http
GET /checkout/{cart_id}
```

#### 설명

활성 장바구니, 장바구니 항목, 사용자 정보, 사용 가능한 쿠폰 목록을 한 번에 반환한다.

쿠폰 포함 조건:

- `coupon_status='active'`
- 유효기간 내
- 현재 장바구니 총액이 `minimum_order_amount` 이상

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

### 6-2. 쿠폰 적용

#### Endpoint

```http
POST /carts/{cart_id}/apply-coupon
```

#### 설명

장바구니 총액 기준으로 쿠폰 적용 가능 여부를 판단하고 할인 결과를 반환한다.

현재 지원하는 `coupon_type`:

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

## 7. 주문 / 결제

### 7-1. 주문 생성

#### Endpoint

```http
POST /orders
```

#### 설명

활성 장바구니를 주문으로 전환한다.

주문 생성 시:

- `orders`에는 `user_id`, `cart_id`, `coupon_id`, `subtotal_amount`, `discount_amount`, `total_amount`, `currency` 저장
- `order_items`에는 `discount_amount`, `final_item_amount`, `line_total`까지 포함해 생성
- 이후 장바구니 상태를 `checked_out`으로 변경

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

주문 생성 실패:

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

### 7-2. 결제 성공/실패 시뮬레이션

#### Endpoint

```http
POST /payments/simulate
```

#### 설명

주문의 현재 상태를 확인한 뒤 결제 결과를 시뮬레이션한다.

결제 가능 조건:

- 주문 상태가 `created` 또는 `payment_failed`

결과 반영:

- 성공 시 주문 상태 `paid`
- 실패 시 주문 상태 `payment_failed`

`payments`에는 `paid_amount`, `pg_provider`, `transaction_id`, `failure_code` 등이 저장된다.

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

### 7-3. 주문 내역 조회

#### Endpoint

```http
GET /orders?user_id={user_id}
```

#### 설명

사용자 주문 목록을 최신순으로 반환한다.

동작 방식:

- 각 주문은 최신 결제 상태를 서브쿼리로 조회
- `order_items`를 다시 조회해 항목 목록 포함
- `coupon_id` 기준으로 `coupons`와 조인해 `coupon_name` 반환

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

## 8. 리뷰(Review)

### 8-1. 리뷰 생성

#### Endpoint

```http
POST /reviews
```

#### 설명

리뷰는 반드시 **구매 완료된 주문 항목(`order_item_id`) 기준**으로만 생성할 수 있다.

검증 순서:

1. 사용자 존재
2. 상품 존재/활성
3. 구매 이력 존재
4. 동일 `order_item_id` 중복 리뷰 여부 확인

`review_status` 기본값은 `visible`이다.

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

### 8-2. 리뷰 수정

#### Endpoint

```http
PATCH /reviews/{review_id}
```

#### 설명

리뷰 작성자 본인만 수정할 수 있다. 이미 `deleted` 상태인 리뷰는 수정할 수 없다.

수정 가능한 필드:

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

타인 리뷰 수정 시도:

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

삭제된 리뷰 수정 시도:

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

### 8-3. 리뷰 삭제

#### Endpoint

```http
DELETE /reviews/{review_id}
```

#### 설명

리뷰는 물리 삭제가 아니라 `review_status='deleted'`로 soft delete 처리된다.

제약 조건:

- 작성자 본인만 삭제 가능
- 이미 삭제된 리뷰는 다시 삭제 불가
- 현재 구현은 요청 바디의 `user_id`로 소유자 검증 수행

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

타인 리뷰 삭제 시도:

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

## 9. 상태값 표준

현재 문서 기준 상태값 표준은 아래와 같다.

- `users.user_status`: `active`
- `products.product_status`: `on_sale`, `out_of_stock`
- `carts.cart_status`: `active`, `checked_out`
- `orders.order_status`: `created`, `paid`, `payment_failed`
- `coupons.coupon_status`: `active`
- `payments.payment_status`: `requested`, `paid`, `failed`
- `reviews.review_status`: `visible`, `deleted`

---

## 10. 비고

- `POST /carts`는 현재 구현상 “생성 또는 기존 활성 장바구니 반환” 동작을 하나의 API로 처리하므로, 성공 응답을 `200 OK`로 문서화
- `GET /products/{product_id}`는 초안에는 포함되어 있으나, 이번 최종본에서는 실제 route/schema 응답이 고정되지 않아 `TBD`로 남겨둠
- `DELETE /reviews/{review_id}`는 soft delete 방식이며, 요청 바디의 `user_id`를 통해 소유자 검증을 수행
