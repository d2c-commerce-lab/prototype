---
title: State and Error Message Consistency Checklist
version: v1.0
language: en
domain: backend
doc_type: consistency-checklist
---

# State and Error Message Consistency Checklist

## 0. Purpose

This document is the final checklist for D2C-53. Based on the results of the **API specification finalization** and the **manual validation of the core user flow**, it verifies whether backend **state values** and **error messages** are designed and implemented consistently across the project.

The goals of this document are:

- verify that domain-level state values are used with the same meaning
- verify that the same type of error returns a consistent status code / message pattern
- classify mismatches found during manual validation into **documentation fix / code fix / no issue**
- stabilize the response contract used for frontend integration before closing D2C-53

---

## 1. How to Use

For each item, reflect the actual validation result using one of the following judgments.

- `[x] No issue`
- `[ ] Needs additional verification`
- `Action needed: fix documentation`
- `Action needed: fix code`

Or write the result directly in the `Verdict`, `Actual`, and `Action` columns of each table.

Recommended recording method:

- **Actual**: response value or state value observed during manual validation
- **Expected**: expected value from the API specification
- **Verdict**: pass / fail / re-check
- **Action**: no issue / fix documentation / fix code / split into follow-up task

---

## 2. State Value Consistency Checklist

### 2-1. Users

| Item | Expected Value | Check Point | Actual | Verdict | Action |
|---|---|---|---|---|---|
| `users.user_status` | `active` | verify that the same value is used in both sign-up and login responses |  |  |  |

Check notes:
- after successful sign-up, `user_status = active`
- after successful login, `user_status = active`

### 2-2. Products

| Item | Expected Value | Check Point | Actual | Verdict | Action |
|---|---|---|---|---|---|
| `products.product_status` | `on_sale`, `out_of_stock` | verify that the product-list response returns the documented state values |  |  |  |
| `products.is_active` | `true`, `false` | verify that inactive products are excluded from list/cart-eligible flow |  |  |  |

Check notes:
- product-list results and cart eligibility conditions should match
- `on_sale` products should be usable in the normal purchase flow

### 2-3. Carts

| Item | Expected Value | Check Point | Actual | Verdict | Action |
|---|---|---|---|---|---|
| `carts.cart_status` | `active`, `checked_out` | verify that the cart starts as `active` and becomes `checked_out` after order creation |  |  |  |

Check notes:
- immediately after `POST /carts`, the value should be `active`
- after `POST /orders`, the related cart should be transitioned to `checked_out`

### 2-4. Orders

| Item | Expected Value | Check Point | Actual | Verdict | Action |
|---|---|---|---|---|---|
| `orders.order_status` | `created`, `paid`, `payment_failed` | verify that state transitions after order creation and payment success/failure match the specification |  |  |  |

Check notes:
- immediately after order creation: `created`
- after successful payment: `paid`
- after failed payment: `payment_failed`

### 2-5. Coupons

| Item | Expected Value | Check Point | Actual | Verdict | Action |
|---|---|---|---|---|---|
| `coupons.coupon_status` | `active` | verify that only active coupons are exposed in checkout and coupon-application flows |  |  |  |

Check notes:
- the current document standard is `active`
- validity-window logic should work together with this state value

### 2-6. Payments

| Item | Expected Value | Check Point | Actual | Verdict | Action |
|---|---|---|---|---|---|
| `payments.payment_status` | `requested`, `paid`, `failed` | verify that payment-simulation responses and order-history results are consistent |  |  |  |

Check notes:
- successful payment response: `paid`
- failed payment response: `failed`
- `payment_status` in order history should match the latest payment result

### 2-7. Reviews

| Item | Expected Value | Check Point | Actual | Verdict | Action |
|---|---|---|---|---|---|
| `reviews.review_status` | `visible`, `deleted` | verify that review creation yields `visible` and review deletion yields `deleted` |  |  |  |

Check notes:
- after successful review creation: `visible`
- review deletion must be soft delete, not physical delete

---

## 3. Error Message Consistency Checklist

### 3-1. Not Found Cases

| Resource / Case | Expected Status | Expected Message | Actual | Verdict | Action |
|---|---:|---|---|---|---|
| missing user | `404` | `User not found` |  |  |  |
| missing product | `404` | `Product not found` |  |  |  |
| missing coupon | `404` | `Coupon not found` |  |  |  |
| missing order | `404` | `Order not found` |  |  |  |
| missing review | `404` | `Review not found` |  |  |  |
| missing active cart | `404` | `Active cart not found` |  |  |  |
| missing cart item | `404` | `Cart item not found` |  |  |  |
| missing active session | `404` | `Active session not found` |  |  |  |

Check notes:
- resource-missing cases should be unified to the `X not found` pattern whenever possible
- only state-qualified cases such as `Active cart not found` and `Active session not found` should remain more specific

### 3-2. Conflict Cases

| Case | Expected Status | Expected Message | Actual | Verdict | Action |
|---|---:|---|---|---|---|
| duplicate sign-up | `409` | `Email already exists` |  |  |  |
| duplicate review creation | `409` | `Review already exists for this order item` |  |  |  |

Check notes:
- duplicate creation / duplicate registration errors should remain `409 Conflict`

### 3-3. Forbidden Cases

| Case | Expected Status | Expected Message | Actual | Verdict | Action |
|---|---:|---|---|---|---|
| update another user's review | `403` | `You can only update your own review` |  |  |  |
| delete another user's review | `403` | `You can only delete your own review` |  |  |  |

Check notes:
- permission errors are most readable when unified under the `You can only ...` pattern

### 3-4. Bad Request Cases

| Case | Expected Status | Expected Message | Actual | Verdict | Action |
|---|---:|---|---|---|---|
| empty cart checkout | `400` | `Cart is empty` |  |  |  |
| coupon minimum order amount not met | `400` | `Cart total does not meet coupon minimum order amount` |  |  |  |
| non-payable order | `400` | `Order is not payable` |  |  |  |
| review without purchase history | `400` | `Review can only be created for purchased products` |  |  |  |
| update deleted review | `400` | `Deleted review cannot be updated` |  |  |  |
| delete already deleted review | `400` | `Review is already deleted` |  |  |  |
| unsupported coupon type | `400` | `Unsupported coupon type` |  |  |  |

Check notes:
- state mismatches, domain-rule violations, and unmet preconditions should remain `400 Bad Request`
- if similar cases use different message styles, they should be unified

### 3-5. Unauthorized Cases

| Case | Expected Status | Expected Message | Actual | Verdict | Action |
|---|---:|---|---|---|---|
| login failure | `401` | `Invalid email or password` |  |  |  |

Check notes:
- authentication failure should continue to avoid distinguishing email from password

### 3-6. Internal Server Error Cases

| Case | Expected Status | Expected Message | Actual | Verdict | Action |
|---|---:|---|---|---|---|
| user creation failure | `500` | `Failed to create user` |  |  |  |
| session creation failure | `500` | `Failed to create session` |  |  |  |
| cart creation failure | `500` | `Failed to create cart` |  |  |  |
| cart item add failure | `500` | `Failed to add item to cart` |  |  |  |
| cart item update failure | `500` | `Failed to update cart item` |  |  |  |
| order creation failure | `500` | `Failed to create order` |  |  |  |
| order item creation failure | `500` | `Failed to create order item` |  |  |  |
| payment creation failure | `500` | `Failed to create payment` |  |  |  |
| review creation failure | `500` | `Failed to create review` |  |  |  |
| review update failure | `500` | `Failed to update review` |  |  |  |
| review deletion failure | `500` | `Failed to delete review` |  |  |  |

Check notes:
- internal processing failures are easiest to read when kept in the `Failed to ...` pattern
- if the documented messages differ from actual behavior, prioritize documenting or fixing them

---

## 4. Consolidated Table for Actual Validation Results

| Type | Item | Expected | Actual | Verdict | Action |
|---|---|---|---|---|---|
| State | `user_status` after sign-up | `active` |  |  |  |
| State | `cart_status` after cart creation | `active` |  |  |  |
| State | `order_status` after order creation | `created` |  |  |  |
| State | `payment_status` after successful payment | `paid` |  |  |  |
| State | `review_status` after review creation | `visible` |  |  |  |
| State | `review_status` after review deletion | `deleted` |  |  |  |
| Error | duplicate sign-up | `409 / Email already exists` |  |  |  |
| Error | empty cart checkout | `400 / Cart is empty` |  |  |  |
| Error | coupon minimum not met | `400 / Cart total does not meet coupon minimum order amount` |  |  |  |
| Error | non-payable order retry | `400 / Order is not payable` |  |  |  |
| Error | review without purchase history | `400 / Review can only be created for purchased products` |  |  |  |
| Error | duplicate review creation | `409 / Review already exists for this order item` |  |  |  |
| Error | update another user's review | `403 / You can only update your own review` |  |  |  |
| Error | delete another user's review | `403 / You can only delete your own review` |  |  |  |

---

## 5. Action Rules for Mismatches

### 5-1. Fix Documentation

Classify an issue as a documentation fix in the following cases.

- the actual API response is reasonable, but the wording in the specification is outdated
- the status code is correct, but the example JSON is stale
- the real response field name is correct, but the document is missing it

Examples:
- the document says `201`, but the intended implementation behavior is actually `200`
- descriptive text still uses an older state-value name

### 5-2. Fix Code

Classify an issue as a code fix in the following cases.

- the same type of error returns different status codes
- the same domain state is expressed differently across APIs
- a response field differs from the documented contract in a way that may confuse frontend integration
- an error message is excessively inconsistent or unclear

### 5-3. Split into Follow-Up Task

Split the issue into a follow-up task after D2C-53 in the following cases.

- the domain rule itself needs redesign
- the API response contract requires broader revision
- an unimplemented / TBD API still needs formal finalization

Examples:
- finalize the detailed response structure for `GET /products/{product_id}`
- reconsider the use of request bodies for `DELETE`
- review the need for expanded auth / authorization design

---

## 6. Final Verdict Section

### 6-1. Final Verdict for State Value Consistency

- [ ] all items consistent
- [ ] minor documentation fixes required
- [ ] code fixes required
- [ ] follow-up task required

Memo:

```text
- 
```

### 6-2. Final Verdict for Error Message Consistency

- [ ] all items consistent
- [ ] minor documentation fixes required
- [ ] code fixes required
- [ ] follow-up task required

Memo:

```text
- 
```

### 6-3. D2C-53 Closure Decision

- [ ] ready to close
- [ ] can close after minor fixes
- [ ] close after follow-up fixes are completed

Memo:

```text
- 
```
