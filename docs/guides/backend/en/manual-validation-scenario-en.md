---
title: Manual Validation Scenario for the Core User Flow
version: v1.0
language: en
domain: backend
doc_type: validation-scenario
---

# Manual Validation Scenario for the Core User Flow

## 0. Purpose

This document defines the procedure for manually validating whether the currently implemented backend API can complete the **full core purchase flow from start to finish**.  
The validation has three main goals.

- verify that actual request/response behavior matches the API specification
- verify that key state values transition consistently throughout the flow
- verify that the core user path is not blocked before frontend integration

---

## 1. Scope

This document covers the following normal flow.

- sign up
- login
- start session
- get categories
- get product list
- create cart
- add item to cart
- get cart detail
- enter checkout
- apply coupon
- create order
- simulate successful payment
- get order history
- create review
- update review
- delete review
- end session

It also includes the following exception flow as supplemental validation.

- duplicate sign-up
- empty cart checkout
- coupon minimum order amount not met
- payment attempt on a non-payable order
- review creation without purchase history
- duplicate review creation
- update/delete another user's review

This scope matches the major endpoints currently included in the API specification.

---

## 2. Prerequisites

### 2-1. Server

The backend server must already be running.

Example:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 2-2. Data Preparation

The following conditions must be satisfied.

- `categories` seed data exists
- `products` seed data exists
- `coupons` seed data exists
- at least one active product exists for order creation
- at least one valid coupon in `active` state exists within its validity window

### 2-3. Validation Tools

Use one of the following.

- Swagger UI (`/docs`)
- PowerShell `Invoke-RestMethod`
- `curl`
- Postman

### 2-4. Shared PowerShell Variables

Declare the following variables first, then update them step by step as the validation proceeds.

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

### 2-5. Logging Method

Record the following for every step.

- request endpoint / method
- request body or query parameter
- response status code
- key response fields
- verdict: pass / fail
- notes: mismatch or follow-up observation

---

## 3. Shared Validation Criteria

### 3-1. Success Criteria

- the actual status code matches the API specification
- key response fields are not missing
- required identifiers for the next step (`user_id`, `session_id`, `cart_id`, `order_id`, `order_item_id`, `review_id`) are successfully obtained

### 3-2. Failure Criteria

- a status code different from the specification is returned
- a required response field is missing
- a returned state value differs from the documented expectation
- the flow cannot proceed to the next step

### 3-3. State Value Checkpoints

Use the following state values as the baseline.

- `users.user_status = active`
- `carts.cart_status = active → checked_out`
- `orders.order_status = created → paid` or `payment_failed`
- `payments.payment_status = paid` or `failed`
- `reviews.review_status = visible → deleted`

---

## 4. Manual Validation Scenario for the Normal Flow

### Scenario A. End-to-end purchase flow from sign-up to review deletion

### Step A-1. Sign Up

**Goal**  
Create a new user and obtain `user_id`.

**Command**

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

**Expected Result**

- Status: `201 Created`
- `user_id` is returned
- `user_status = "active"`

**Validation Points**

- the same `user_id` should be used throughout the user flow
- the response structure should match the API specification

### Step A-2. Login

**Goal**  
Verify that the newly registered account can log in.

**Command**

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

**Expected Result**

- Status: `200 OK`
- the returned `user_id` matches the one from the sign-up step
- `message = "Login successful"`

**Validation Points**

- authentication flow works correctly
- the email/password pair is validated correctly

### Step A-3. Start Session

**Goal**  
Create a user session and obtain `session_id`.

**Command**

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

**Expected Result**

- Status: `201 Created`
- `session_id` is returned
- `session_end_at = null`

**Validation Points**

- the session-start API works correctly
- the user session is recorded as the starting point of the purchase flow

### Step A-4. Get Categories

**Goal**  
Verify that catalog entry is available.

**Command**

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

**Expected Result**

- Status: `200 OK`
- an array is returned
- at least one active category exists

**Validation Points**

- category seed data is available
- the `category_status = active` structure is correct

### Step A-5. Get Product List

**Goal**  
Identify a purchasable product.

**Command**

```powershell
$productsResponse = Invoke-RestMethod `
  -Method Get `
  -Uri "$BASE_URL/products"

$productsResponse
$PRODUCT_ID = $productsResponse[0].product_id
```

If category-filtered retrieval is needed, use the following.

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

or

```http
GET /products?category_id={CATEGORY_ID}
```

**Expected Result**

- Status: `200 OK`
- at least one active product exists
- secure the `product_id` for later steps
- ideally use a product with `product_status = "on_sale"`

**Validation Points**

- product-list API works correctly
- `sale_price`, `currency`, and `is_active` fields exist as expected

### Step A-6. Create Cart

**Goal**  
Secure an active cart.

**Command**

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

**Expected Result**

- Status: `200 OK`
- `cart_id` is returned
- `cart_status = "active"`

**Validation Points**

- verify that both new cart creation and active-cart reuse return `200 OK` in the current implementation

### Step A-7. Add Item to Cart

**Goal**  
Add a product to the cart.

**Command**

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

**Expected Result**

- Status: `200 OK`
- `cart_item_id` is returned
- `quantity = 2`
- `unit_price` matches the product’s `sale_price`

**Validation Points**

- verify that pricing is correctly copied from product data
- verify that the cart-item create/merge logic works correctly

### Step A-8. Get Cart Detail

**Goal**  
Verify cart total calculation.

**Command**

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

**Expected Result**

- Status: `200 OK`
- `total_items >= 1`
- `total_quantity = 2`
- `total_amount = quantity * unit_price`
- `items[0].line_total` exists

**Validation Points**

- verify amount calculation logic
- verify that `product_name` is joined correctly

### Step A-9. Enter Checkout

**Goal**  
Validate checkout-entry data.

**Command**

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

**Expected Result**

- Status: `200 OK`
- user information is included
- cart items are included
- available coupons may be included

**Validation Points**

- verify the structure of `user`, `items`, and `available_coupons`
- verify that `total_amount` matches the cart-detail response

### Step A-10. Apply Coupon

**Goal**  
Validate discount calculation.

**Command**

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

**Expected Result**

- Status: `200 OK`
- `discount_amount > 0`
- `final_amount = total_amount - discount_amount`

**Validation Points**

- verify that the minimum order amount condition is satisfied
- verify that coupon-type calculation works correctly

### Step A-11. Create Order

**Goal**  
Convert the cart into an order.

**Command**

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

**Expected Result**

- Status: `201 Created`
- `order_id` is returned
- `order_status = "created"`
- `subtotal_amount`, `discount_amount`, and `total_amount` are calculated correctly
- the `items` array is included

**Validation Points**

- the cart state should transition after order creation
- secure the `order_id` for payment simulation

### Step A-12. Simulate Successful Payment

**Goal**  
Move the order into `paid` state.

**Command**

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

**Expected Result**

- Status: `200 OK`
- `payment_status = "paid"`
- `approved_amount = total_amount`
- `failed_reason = null`

**Validation Points**

- verify through later retrieval that successful payment is reflected as `paid` in the order state

### Step A-13. Get Order History

**Goal**  
Verify that the completed order appears in the user’s order history.

**Command**

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

**Expected Result**

- Status: `200 OK`
- `total_orders >= 1`
- the most recent order has `order_status = "paid"`
- `payment_status = "paid"`
- `coupon_name` is correctly reflected

**Validation Points**

- verify the join result across order, payment, coupon, and order item data
- secure the `order_item_id` for review creation

### Step A-14. Create Review

**Goal**  
Validate review creation based on purchase history.

**Command**

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

**Expected Result**

- Status: `201 Created`
- `review_id` is returned
- `review_status = "visible"`

**Validation Points**

- verify that review creation is correctly restricted to completed purchase items

### Step A-15. Update Review

**Goal**  
Validate that the author can update their own review.

**Command**

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

**Expected Result**

- Status: `200 OK`
- `rating = 4`
- `review_title = "Updated title"`
- `message = "Review updated successfully"`

**Validation Points**

- verify that review update is allowed before soft deletion
- verify that ownership validation works correctly

### Step A-16. Delete Review

**Goal**  
Validate review soft delete.

**Command**

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

**Expected Result**

- Status: `200 OK`
- `review_status = "deleted"`

**Validation Points**

- verify that this is a state change rather than a physical delete
- re-deleting the same review later should fail

### Step A-17. End Session

**Goal**  
Validate session termination at the end of the user flow.

**Command**

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

**Expected Result**

- Status: `200 OK`
- `session_end_at` is populated with a non-null value

**Validation Points**

- verify that the session end time is correctly recorded

---

## 5. Manual Validation Scenario for the Exception Flow

### Scenario B-1. Duplicate Sign-Up

Attempt sign-up again using the same email.

**Command**

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri "$BASE_URL/auth/signup" `
  -ContentType "application/json" `
  -Body '{"email":"manual_flow_user@example.com","user_name":"manual-flow-user","password":"Password123!","marketing_opt_in_yn":true}'
```

**Expected Result**

- Status: `409 Conflict`
- `detail = "Email already exists"`

### Scenario B-2. Empty Cart Checkout

Create a new cart and enter checkout without adding any items.

**Command**

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

**Expected Result**

- Status: `400 Bad Request`
- `detail = "Cart is empty"`

### Scenario B-3. Coupon Minimum Order Amount Not Met

Apply a coupon with a minimum-order condition to a cart with a small total.

**Command**

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

**Expected Result**

- Status: `400 Bad Request`
- `detail = "Cart total does not meet coupon minimum order amount"`

### Scenario B-4. Payment Attempt on a Non-Payable Order

Call payment simulation again for an order that is already in `paid` state.

**Command**

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

**Expected Result**

- Status: `400 Bad Request`
- `detail = "Order is not payable"`

### Scenario B-5. Review Creation Without Purchase History

Create a review using a product or `order_item_id` that does not belong to an actual purchase.

**Command**

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

**Expected Result**

- Status: `400 Bad Request`
- `detail = "Review can only be created for purchased products"`

### Scenario B-6. Duplicate Review Creation

Create two reviews for the same `order_item_id`.

**Command**

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

**Expected Result**

- Status: `409 Conflict`
- `detail = "Review already exists for this order item"`

### Scenario B-7. Update/Delete Another User's Review

Use a different `user_id` to update or delete the same `review_id`.

**Command**

Create another user first:

```powershell
$otherUserResponse = Invoke-RestMethod `
  -Method Post `
  -Uri "$BASE_URL/auth/signup" `
  -ContentType "application/json" `
  -Body '{"email":"manual_flow_other_user@example.com","user_name":"manual-flow-other-user","password":"Password123!","marketing_opt_in_yn":false}'

$OTHER_USER_ID = $otherUserResponse.user_id
```

Update attempt:

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

Delete attempt:

```powershell
Invoke-RestMethod `
  -Method Delete `
  -Uri "$BASE_URL/reviews/$REVIEW_ID" `
  -ContentType "application/json" `
  -Body (@{
    user_id = $OTHER_USER_ID
  } | ConvertTo-Json)
```

**Expected Result**

- update: `403 Forbidden`, `You can only update your own review`
- delete: `403 Forbidden`, `You can only delete your own review`

---

## 6. Validation Result Template

Use the following format to record results.

```md
## [Validation Result] Step A-11 Create Order

- Request: POST /orders
- Input:
  - cart_id: ...
  - coupon_name: ...
- Expected:
  - 201 Created
  - order_status = created
- Actual:
  - Status: ...
  - order_status: ...
  - order_id: ...
- Result: Pass / Fail
- Notes:
  - whether it matches the specification
  - whether required fields are missing
```

---

## 7. Completion Criteria

According to this document, D2C-53 manual validation for the **core user flow** is considered complete only if all of the following are satisfied.

- normal flow A-1 ~ A-17 all pass
- exception flow B-1 ~ B-7 all return the expected status / message
- state transitions match the API specification
- the identifier chain (`user_id → cart_id → order_id → order_item_id → review_id`) is not broken
- mismatches discovered during validation are captured as separate follow-up items

