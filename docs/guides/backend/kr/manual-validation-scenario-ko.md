---
title: 핵심 사용자 흐름 수동 검증 시나리오
version: v1.0
language: ko
domain: backend
doc_type: validation-scenario
---

# 핵심 사용자 흐름 수동 검증 시나리오 문서

## 0. 목적

본 문서는 현재 구현된 백엔드 API가 **핵심 사용자 구매 흐름을 끝까지 정상적으로 수행하는지** 수동으로 검증하기 위한 절차를 정의한다.  
검증 목적은 아래 세 가지다.

- API 명세서의 요청/응답 구조가 실제 동작과 일치하는지 확인
- 주요 상태값이 흐름에 따라 일관되게 전이되는지 확인
- 프론트엔드 연동 전에 사용자 핵심 플로우가 막힘 없이 이어지는지 확인

---

## 1. 검증 범위

본 문서의 검증 범위는 아래 흐름을 포함한다.

- 회원가입
- 로그인
- 세션 시작
- 카테고리 조회
- 상품 목록 조회
- 장바구니 생성
- 장바구니 담기
- 장바구니 조회
- 체크아웃 진입
- 쿠폰 적용
- 주문 생성
- 결제 성공 시뮬레이션
- 주문 내역 조회
- 리뷰 생성
- 리뷰 수정
- 리뷰 삭제
- 세션 종료

보조 검증으로 아래 예외 흐름도 포함한다.

- 중복 회원가입
- 빈 장바구니 체크아웃
- 최소 주문 금액 미달 쿠폰 적용
- 결제 불가 상태 주문 결제 시도
- 구매 이력 없는 리뷰 작성
- 중복 리뷰 작성
- 타인 리뷰 수정/삭제

이 범위는 현재 API 명세서에 포함된 주요 엔드포인트와 동일하다.

---

## 2. 사전 준비

### 2-1. 서버 실행

백엔드 서버가 실행 중이어야 한다.

예시:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 2-2. 데이터 준비

아래 조건이 만족되어야 한다.

- `categories` seed 데이터 존재
- `products` seed 데이터 존재
- `coupons` seed 데이터 존재
- 주문 생성에 사용할 활성 상품이 존재
- 유효기간 내 `active` 상태 쿠폰이 존재

### 2-3. 검증 도구

아래 중 하나를 사용한다.

- Swagger UI (`/docs`)
- PowerShell `Invoke-RestMethod`
- `curl`
- Postman

### 2-4. PowerShell 공통 변수 선언

아래 변수들을 먼저 선언한 뒤, 각 단계에서 값을 갱신하면서 사용한다.

```powershell
$BASE_URL = "http://localhost:8000"

$USER_ID = ""
$SESSION_ID = ""
$CATEGORY_ID = ""
$PRODUCT_ID = ""
$CART_ID = ""
$CART_ITEM_ID = ""
$ORDER_ID = ""
$ORDER_ITEM_ID = ""
$REVIEW_ID = ""
```

### 2-5. 기록 방식

각 단계마다 아래를 기록한다.

- 요청 endpoint / method
- 요청 body 또는 query param
- 응답 status code
- 응답 핵심 필드
- 판정: 정상 / 비정상
- 비고: 불일치 사항

---

## 3. 공통 검증 기준

### 3-1. 성공 기준

- API 명세서에 정의된 status code와 실제 응답이 일치한다
- 응답 body의 주요 필드가 누락되지 않는다
- 다음 단계 수행에 필요한 식별자(`user_id`, `session_id`, `cart_id`, `order_id`, `order_item_id`, `review_id`)가 정상적으로 확보된다

### 3-2. 실패 기준

- 명세서와 다른 status code 반환
- 필수 응답 필드 누락
- 상태값이 명세서와 다름
- 다음 단계로 흐름이 이어지지 않음

### 3-3. 상태값 점검 기준

현재 주요 상태값은 아래를 기준으로 확인한다.

- `users.user_status = active`
- `carts.cart_status = active → checked_out`
- `orders.order_status = created → paid` 또는 `payment_failed`
- `payments.payment_status = paid` 또는 `failed`
- `reviews.review_status = visible → deleted`

---

## 4. 정상 흐름 수동 검증 시나리오

### 시나리오 A. 회원가입부터 리뷰 삭제까지의 정상 구매 플로우

### Step A-1. 회원가입

**목적**  
신규 사용자 생성 및 `user_id` 확보

**실행 명령어**

```powershell
$signupResponse = Invoke-RestMethod `
  -Method Post `
  -Uri "$BASE_URL/auth/signup" `
  -ContentType "application/json" `
  -Body '{"email":"manual_flow_user@example.com","user_name":"manual-flow-user","password":"Password123!","marketing_opt_in_yn":true}'

$signupResponse
$USER_ID = $signupResponse.user_id
```

**Request**

```http
POST /auth/signup
{
  "email": "manual_flow_user@example.com",
  "user_name": "manual-flow-user",
  "password": "Password123!",
  "marketing_opt_in_yn": true
}
```

**기대 결과**

- Status: `201 Created`
- `user_id` 반환
- `user_status = "active"`

**검증 포인트**

- 이후 모든 사용자 흐름에서 이 `user_id`를 사용한다
- 응답 구조가 API 명세서와 일치한다

### Step A-2. 로그인

**목적**  
회원가입한 계정으로 로그인 가능한지 검증

**실행 명령어**

```powershell
$loginResponse = Invoke-RestMethod `
  -Method Post `
  -Uri "$BASE_URL/auth/login" `
  -ContentType "application/json" `
  -Body '{"email":"manual_flow_user@example.com","password":"Password123!"}'

$loginResponse
```

**Request**

```http
POST /auth/login
{
  "email": "manual_flow_user@example.com",
  "password": "Password123!"
}
```

**기대 결과**

- Status: `200 OK`
- 반환된 `user_id`가 회원가입 단계의 `user_id`와 일치
- `message = "Login successful"`

**검증 포인트**

- 인증 흐름 정상 여부
- 이메일/비밀번호 조합 일치 여부

### Step A-3. 세션 시작

**목적**  
사용자 세션 생성 및 `session_id` 확보

**실행 명령어**

```powershell
$sessionStartResponse = Invoke-RestMethod `
  -Method Post `
  -Uri "$BASE_URL/sessions" `
  -ContentType "application/json" `
  -Body (@{
    user_id = $USER_ID
    campaign_id = $null
    anonymous_id = "anon-manual-001"
    platform = "web"
    device_type = "desktop"
    os_type = "windows"
    browser_type = "chrome"
    traffic_source = "direct"
    traffic_medium = "none"
    landing_page_url = "/"
    referrer_url = $null
  } | ConvertTo-Json)

$sessionStartResponse
$SESSION_ID = $sessionStartResponse.session_id
```

**Request**

```http
POST /sessions
{
  "user_id": "{USER_ID}",
  "campaign_id": null,
  "anonymous_id": "anon-manual-001",
  "platform": "web",
  "device_type": "desktop",
  "os_type": "windows",
  "browser_type": "chrome",
  "traffic_source": "direct",
  "traffic_medium": "none",
  "landing_page_url": "/",
  "referrer_url": null
}
```

**기대 결과**

- Status: `201 Created`
- `session_id` 반환
- `session_end_at = null`

**검증 포인트**

- 세션 시작 API 정상 동작
- 사용자 세션이 구매 흐름 시작점으로 기록되는지 확인

### Step A-4. 카테고리 조회

**목적**  
카탈로그 진입 가능 여부 확인

**실행 명령어**

```powershell
$categoriesResponse = Invoke-RestMethod `
  -Method Get `
  -Uri "$BASE_URL/categories"

$categoriesResponse
$CATEGORY_ID = $categoriesResponse[0].category_id
```

**Request**

```http
GET /categories
```

**기대 결과**

- Status: `200 OK`
- 배열 반환
- 최소 1개 이상의 활성 카테고리 존재

**검증 포인트**

- 카테고리 데이터 seed 정상 여부
- `category_status = active` 구조 확인

### Step A-5. 상품 목록 조회

**목적**  
구매 가능한 상품 식별

**실행 명령어**

```powershell
$productsResponse = Invoke-RestMethod `
  -Method Get `
  -Uri "$BASE_URL/products"

$productsResponse
$PRODUCT_ID = $productsResponse[0].product_id
```

카테고리 기준 조회가 필요하면 아래를 사용한다.

```powershell
$productsByCategoryResponse = Invoke-RestMethod `
  -Method Get `
  -Uri "$BASE_URL/products?category_id=$CATEGORY_ID"

$productsByCategoryResponse
```

**Request**

```http
GET /products
```

또는

```http
GET /products?category_id={CATEGORY_ID}
```

**기대 결과**

- Status: `200 OK`
- 최소 1개 이상의 활성 상품 존재
- 이후 사용할 `product_id` 확보
- 사용할 상품의 `product_status = "on_sale"` 권장

**검증 포인트**

- 상품 목록 API 정상 동작
- `sale_price`, `currency`, `is_active` 필드 존재 여부 확인

### Step A-6. 장바구니 생성

**목적**  
활성 장바구니 확보

**실행 명령어**

```powershell
$cartResponse = Invoke-RestMethod `
  -Method Post `
  -Uri "$BASE_URL/carts" `
  -ContentType "application/json" `
  -Body (@{
    user_id = $USER_ID
  } | ConvertTo-Json)

$cartResponse
$CART_ID = $cartResponse.cart_id
```

**Request**

```http
POST /carts
{
  "user_id": "{USER_ID}"
}
```

**기대 결과**

- Status: `200 OK`
- `cart_id` 반환
- `cart_status = "active"`

**검증 포인트**

- 현재 구현상 신규 생성 또는 기존 활성 장바구니 반환 모두 `200 OK`인지 확인

### Step A-7. 장바구니 담기

**목적**  
상품을 장바구니에 추가

**실행 명령어**

```powershell
$addCartItemResponse = Invoke-RestMethod `
  -Method Post `
  -Uri "$BASE_URL/carts/$CART_ID/items" `
  -ContentType "application/json" `
  -Body (@{
    product_id = $PRODUCT_ID
    quantity = 2
  } | ConvertTo-Json)

$addCartItemResponse
$CART_ITEM_ID = $addCartItemResponse.cart_item_id
```

**Request**

```http
POST /carts/{CART_ID}/items
{
  "product_id": "{PRODUCT_ID}",
  "quantity": 2
}
```

**기대 결과**

- Status: `200 OK`
- `cart_item_id` 반환
- `quantity = 2`
- `unit_price`가 상품의 `sale_price`와 일치

**검증 포인트**

- 가격이 상품 정보에서 정상 반영되는지
- 장바구니 항목 생성/병합 로직이 동작하는지 확인

### Step A-8. 장바구니 조회

**목적**  
장바구니 총합 계산 검증

**실행 명령어**

```powershell
$getCartResponse = Invoke-RestMethod `
  -Method Get `
  -Uri "$BASE_URL/carts/$CART_ID"

$getCartResponse
```

**Request**

```http
GET /carts/{CART_ID}
```

**기대 결과**

- Status: `200 OK`
- `total_items >= 1`
- `total_quantity = 2`
- `total_amount = quantity * unit_price`
- `items[0].line_total` 존재

**검증 포인트**

- 금액 계산 로직 검증
- `product_name` 조인 여부 확인

### Step A-9. 체크아웃 진입

**목적**  
체크아웃 화면 진입 데이터 검증

**실행 명령어**

```powershell
$checkoutResponse = Invoke-RestMethod `
  -Method Get `
  -Uri "$BASE_URL/checkout/$CART_ID"

$checkoutResponse
```

**Request**

```http
GET /checkout/{CART_ID}
```

**기대 결과**

- Status: `200 OK`
- 사용자 정보 포함
- 장바구니 항목 포함
- 사용 가능한 쿠폰 목록 포함 가능

**검증 포인트**

- `user`, `items`, `available_coupons` 구조 확인
- `total_amount`가 장바구니 조회와 일치하는지 확인

### Step A-10. 쿠폰 적용

**목적**  
할인 계산 검증

**실행 명령어**

```powershell
$applyCouponResponse = Invoke-RestMethod `
  -Method Post `
  -Uri "$BASE_URL/carts/$CART_ID/apply-coupon" `
  -ContentType "application/json" `
  -Body '{"coupon_name":"WELCOME10"}'

$applyCouponResponse
```

**Request**

```http
POST /carts/{CART_ID}/apply-coupon
{
  "coupon_name": "WELCOME10"
}
```

**기대 결과**

- Status: `200 OK`
- `discount_amount > 0`
- `final_amount = total_amount - discount_amount`

**검증 포인트**

- 최소 주문금액 조건 만족 여부
- 쿠폰 타입별 계산 정상 여부

### Step A-11. 주문 생성

**목적**  
장바구니를 주문으로 전환

**실행 명령어**

```powershell
$orderResponse = Invoke-RestMethod `
  -Method Post `
  -Uri "$BASE_URL/orders" `
  -ContentType "application/json" `
  -Body (@{
    cart_id = $CART_ID
    coupon_name = "WELCOME10"
  } | ConvertTo-Json)

$orderResponse
$ORDER_ID = $orderResponse.order_id
$ORDER_ITEM_ID = $orderResponse.items[0].order_item_id
```

**Request**

```http
POST /orders
{
  "cart_id": "{CART_ID}",
  "coupon_name": "WELCOME10"
}
```

**기대 결과**

- Status: `201 Created`
- `order_id` 반환
- `order_status = "created"`
- `subtotal_amount`, `discount_amount`, `total_amount` 계산 일치
- `items` 배열 포함

**검증 포인트**

- 주문 생성 후 장바구니 상태 전환 예정
- 이후 결제 시뮬레이션에 사용할 `order_id` 확보

### Step A-12. 결제 성공 시뮬레이션

**목적**  
주문 상태를 `paid`로 전환

**실행 명령어**

```powershell
$paymentResponse = Invoke-RestMethod `
  -Method Post `
  -Uri "$BASE_URL/payments/simulate" `
  -ContentType "application/json" `
  -Body (@{
    order_id = $ORDER_ID
    payment_method = "card"
    simulate_result = "success"
  } | ConvertTo-Json)

$paymentResponse
```

**Request**

```http
POST /payments/simulate
{
  "order_id": "{ORDER_ID}",
  "payment_method": "card",
  "simulate_result": "success"
}
```

**기대 결과**

- Status: `200 OK`
- `payment_status = "paid"`
- `approved_amount = total_amount`
- `failed_reason = null`

**검증 포인트**

- 결제 성공 후 주문 상태가 `paid`로 반영되는지 후속 조회에서 확인 필요

### Step A-13. 주문 내역 조회

**목적**  
결제 완료된 주문이 사용자 주문 내역에 반영됐는지 검증

**실행 명령어**

```powershell
$orderHistoryResponse = Invoke-RestMethod `
  -Method Get `
  -Uri "$BASE_URL/orders?user_id=$USER_ID"

$orderHistoryResponse
$ORDER_ITEM_ID = $orderHistoryResponse.orders[0].items[0].order_item_id
```

**Request**

```http
GET /orders?user_id={USER_ID}
```

**기대 결과**

- Status: `200 OK`
- `total_orders >= 1`
- 가장 최근 주문의 `order_status = "paid"`
- `payment_status = "paid"`
- `coupon_name` 정상 반영

**검증 포인트**

- 주문/결제/쿠폰/주문항목 조인 결과 확인
- 리뷰 작성을 위한 `order_item_id` 확보

### Step A-14. 리뷰 생성

**목적**  
구매 이력 기반 리뷰 작성 검증

**실행 명령어**

```powershell
$createReviewResponse = Invoke-RestMethod `
  -Method Post `
  -Uri "$BASE_URL/reviews" `
  -ContentType "application/json" `
  -Body (@{
    user_id = $USER_ID
    product_id = $PRODUCT_ID
    order_item_id = $ORDER_ITEM_ID
    rating = 5
    review_title = "Great product"
    review_content = "The product quality is excellent."
  } | ConvertTo-Json)

$createReviewResponse
$REVIEW_ID = $createReviewResponse.review_id
```

**Request**

```http
POST /reviews
{
  "user_id": "{USER_ID}",
  "product_id": "{PRODUCT_ID}",
  "order_item_id": "{ORDER_ITEM_ID}",
  "rating": 5,
  "review_title": "Great product",
  "review_content": "The product quality is excellent."
}
```

**기대 결과**

- Status: `201 Created`
- `review_id` 반환
- `review_status = "visible"`

**검증 포인트**

- 구매 완료 주문 항목 기준 작성 제한이 정상 동작하는지 확인

### Step A-15. 리뷰 수정

**목적**  
본인 리뷰 수정 검증

**실행 명령어**

```powershell
$updateReviewResponse = Invoke-RestMethod `
  -Method Patch `
  -Uri "$BASE_URL/reviews/$REVIEW_ID" `
  -ContentType "application/json" `
  -Body (@{
    user_id = $USER_ID
    rating = 4
    review_title = "Updated title"
    review_content = "Updated content"
  } | ConvertTo-Json)

$updateReviewResponse
```

**Request**

```http
PATCH /reviews/{REVIEW_ID}
{
  "user_id": "{USER_ID}",
  "rating": 4,
  "review_title": "Updated title",
  "review_content": "Updated content"
}
```

**기대 결과**

- Status: `200 OK`
- `rating = 4`
- `review_title = "Updated title"`
- `message = "Review updated successfully"`

**검증 포인트**

- soft delete 전 수정 가능 여부
- 소유자 검증 정상 동작 여부

### Step A-16. 리뷰 삭제

**목적**  
리뷰 soft delete 검증

**실행 명령어**

```powershell
$deleteReviewResponse = Invoke-RestMethod `
  -Method Delete `
  -Uri "$BASE_URL/reviews/$REVIEW_ID" `
  -ContentType "application/json" `
  -Body (@{
    user_id = $USER_ID
  } | ConvertTo-Json)

$deleteReviewResponse
```

**Request**

```http
DELETE /reviews/{REVIEW_ID}
{
  "user_id": "{USER_ID}"
}
```

**기대 결과**

- Status: `200 OK`
- `review_status = "deleted"`

**검증 포인트**

- 물리 삭제가 아닌 상태값 변경인지 확인
- 이후 동일 리뷰 재삭제 시 실패해야 함

### Step A-17. 세션 종료

**목적**  
사용자 흐름 종료 시 세션 종료 처리 검증

**실행 명령어**

```powershell
$endSessionResponse = Invoke-RestMethod `
  -Method Patch `
  -Uri "$BASE_URL/sessions/$SESSION_ID/end"

$endSessionResponse
```

**Request**

```http
PATCH /sessions/{SESSION_ID}/end
```

**기대 결과**

- Status: `200 OK`
- `session_end_at`이 null이 아닌 값으로 채워짐

**검증 포인트**

- 세션 종료 시점 기록 정상 여부

---

## 5. 예외 흐름 수동 검증 시나리오

### 시나리오 B-1. 중복 회원가입

같은 이메일로 다시 회원가입 요청

**실행 명령어**

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri "$BASE_URL/auth/signup" `
  -ContentType "application/json" `
  -Body '{"email":"manual_flow_user@example.com","user_name":"manual-flow-user","password":"Password123!","marketing_opt_in_yn":true}'
```

**기대 결과**

- Status: `409 Conflict`
- `detail = "Email already exists"`

### 시나리오 B-2. 빈 장바구니 체크아웃

새 장바구니 생성 후 아이템 추가 없이 체크아웃 진입

**실행 명령어**

```powershell
$emptyCartResponse = Invoke-RestMethod `
  -Method Post `
  -Uri "$BASE_URL/carts" `
  -ContentType "application/json" `
  -Body (@{
    user_id = $USER_ID
  } | ConvertTo-Json)

$EMPTY_CART_ID = $emptyCartResponse.cart_id

Invoke-RestMethod `
  -Method Get `
  -Uri "$BASE_URL/checkout/$EMPTY_CART_ID"
```

**기대 결과**

- Status: `400 Bad Request`
- `detail = "Cart is empty"`

### 시나리오 B-3. 최소 주문금액 미달 쿠폰 적용

총액이 작은 장바구니에 최소 금액 조건 쿠폰 적용

**실행 명령어**

```powershell
$smallCartResponse = Invoke-RestMethod `
  -Method Post `
  -Uri "$BASE_URL/carts" `
  -ContentType "application/json" `
  -Body (@{
    user_id = $USER_ID
  } | ConvertTo-Json)

$SMALL_CART_ID = $smallCartResponse.cart_id

Invoke-RestMethod `
  -Method Post `
  -Uri "$BASE_URL/carts/$SMALL_CART_ID/items" `
  -ContentType "application/json" `
  -Body (@{
    product_id = $PRODUCT_ID
    quantity = 1
  } | ConvertTo-Json)

Invoke-RestMethod `
  -Method Post `
  -Uri "$BASE_URL/carts/$SMALL_CART_ID/apply-coupon" `
  -ContentType "application/json" `
  -Body '{"coupon_name":"WELCOME10"}'
```

**기대 결과**

- Status: `400 Bad Request`
- `detail = "Cart total does not meet coupon minimum order amount"`

### 시나리오 B-4. 결제 불가 상태 주문 재결제

이미 `paid` 상태가 된 주문에 다시 결제 시뮬레이션 호출

**실행 명령어**

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri "$BASE_URL/payments/simulate" `
  -ContentType "application/json" `
  -Body (@{
    order_id = $ORDER_ID
    payment_method = "card"
    simulate_result = "success"
  } | ConvertTo-Json)
```

**기대 결과**

- Status: `400 Bad Request`
- `detail = "Order is not payable"`

### 시나리오 B-5. 구매 이력 없는 리뷰 작성

구매하지 않은 상품 또는 임의 `order_item_id`로 리뷰 생성

**실행 명령어**

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri "$BASE_URL/reviews" `
  -ContentType "application/json" `
  -Body (@{
    user_id = $USER_ID
    product_id = $PRODUCT_ID
    order_item_id = "99999999-9999-9999-9999-999999999999"
    rating = 5
    review_title = "Invalid review"
    review_content = "Should fail"
  } | ConvertTo-Json)
```

**기대 결과**

- Status: `400 Bad Request`
- `detail = "Review can only be created for purchased products"`

### 시나리오 B-6. 중복 리뷰 작성

같은 `order_item_id`로 리뷰를 두 번 작성

**실행 명령어**

```powershell
$duplicateReviewFirst = Invoke-RestMethod `
  -Method Post `
  -Uri "$BASE_URL/reviews" `
  -ContentType "application/json" `
  -Body (@{
    user_id = $USER_ID
    product_id = $PRODUCT_ID
    order_item_id = $ORDER_ITEM_ID
    rating = 5
    review_title = "First review"
    review_content = "First submit"
  } | ConvertTo-Json)

$duplicateReviewFirst

Invoke-RestMethod `
  -Method Post `
  -Uri "$BASE_URL/reviews" `
  -ContentType "application/json" `
  -Body (@{
    user_id = $USER_ID
    product_id = $PRODUCT_ID
    order_item_id = $ORDER_ITEM_ID
    rating = 4
    review_title = "Second review"
    review_content = "Second submit"
  } | ConvertTo-Json)
```

**기대 결과**

- Status: `409 Conflict`
- `detail = "Review already exists for this order item"`

### 시나리오 B-7. 타인 리뷰 수정/삭제

다른 `user_id`로 같은 `review_id` 수정 또는 삭제

**실행 명령어**

먼저 타인 사용자 생성:

```powershell
$otherUserResponse = Invoke-RestMethod `
  -Method Post `
  -Uri "$BASE_URL/auth/signup" `
  -ContentType "application/json" `
  -Body '{"email":"manual_flow_other_user@example.com","user_name":"manual-flow-other-user","password":"Password123!","marketing_opt_in_yn":false}'

$OTHER_USER_ID = $otherUserResponse.user_id
```

타인 리뷰 수정 시도:

```powershell
Invoke-RestMethod `
  -Method Patch `
  -Uri "$BASE_URL/reviews/$REVIEW_ID" `
  -ContentType "application/json" `
  -Body (@{
    user_id = $OTHER_USER_ID
    rating = 1
    review_title = "Hijacked title"
    review_content = "Hijacked content"
  } | ConvertTo-Json)
```

타인 리뷰 삭제 시도:

```powershell
Invoke-RestMethod `
  -Method Delete `
  -Uri "$BASE_URL/reviews/$REVIEW_ID" `
  -ContentType "application/json" `
  -Body (@{
    user_id = $OTHER_USER_ID
  } | ConvertTo-Json)
```

**기대 결과**

- 수정: `403 Forbidden`, `You can only update your own review`
- 삭제: `403 Forbidden`, `You can only delete your own review`

---

## 6. 검증 결과 기록 템플릿

아래 형식으로 결과를 남기면 된다.

```md
## [검증 결과] Step A-11 주문 생성

- 요청: POST /orders
- 입력:
  - cart_id: ...
  - coupon_name: ...
- 기대 결과:
  - 201 Created
  - order_status = created
- 실제 결과:
  - Status: ...
  - order_status: ...
  - order_id: ...
- 판정: 정상 / 비정상
- 비고:
  - 명세와 일치 여부
  - 필드 누락 여부
```

---

## 7. 최종 완료 기준

이 문서 기준으로 D2C-53의 **핵심 사용자 흐름 수동 검증**이 완료됐다고 보려면 아래를 만족해야 한다.

- 정상 흐름 A-1 ~ A-17이 모두 통과
- 예외 흐름 B-1 ~ B-7이 모두 기대한 status / message로 반환
- 상태값 전이가 명세서와 일치
- 식별자 흐름(`user_id → cart_id → order_id → order_item_id → review_id`)이 끊기지 않음
- 검증 중 발견된 불일치가 별도 수정 목록으로 정리됨

