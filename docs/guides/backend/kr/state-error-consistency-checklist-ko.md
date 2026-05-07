---
title: 상태값 및 에러 메시지 일관성 점검표
version: v1.0
language: ko
domain: backend
doc_type: consistency-checklist
---

# 상태값 / 에러 메시지 일관성 점검표

## 0. 문서 목적

본 문서는 D2C-53 단계에서 수행한 **API 명세 정리** 및 **핵심 사용자 흐름 수동 검증** 결과를 바탕으로, 현재 백엔드 API의 **상태값(state)** 과 **에러 메시지(error message)** 가 프로젝트 전반에서 일관되게 설계·구현되었는지 점검하기 위한 최종 문서다.

본 문서의 목적은 아래와 같다.

- 도메인별 상태값이 동일한 의미로 사용되는지 확인
- 같은 유형의 오류가 동일한 status code / message 패턴으로 반환되는지 확인
- 수동 검증 과정에서 발견한 차이를 **문서 수정 / 코드 수정 / 이상 없음**으로 분류
- D2C-53 종료 전, 프론트엔드 연동 기준이 되는 응답 계약을 안정화

---

## 1. 사용 방법

각 항목에 대해 실제 검증 결과를 반영하여 아래 기준으로 판정한다.

- `[x] 이상 없음`
- `[ ] 추가 확인 필요`
- `조치 필요: 문서 수정`
- `조치 필요: 코드 수정`

또는 표의 `판정`, `실제 결과`, `조치` 컬럼에 직접 기입한다.

권장 기록 방식:

- **실제 결과**: 수동 검증 중 확인한 응답값 또는 상태값
- **기대 결과**: API 명세서 기준 기대값
- **판정**: 정상 / 비정상 / 재확인 필요
- **조치**: 이상 없음 / 문서 수정 / 코드 수정 / 후속 태스크 분리

---

## 2. 상태값 일관성 점검표

### 2-1. Users

| 항목 | 기대 기준값 | 점검 기준 | 실제 결과 | 판정 | 조치 |
|---|---|---|---|---|---|
| `users.user_status` | `active` | 회원가입 응답과 로그인 응답에서 동일하게 사용되는지 확인 |  |  |  |

체크 메모:
- 회원가입 성공 시 `user_status = active`
- 로그인 성공 시 `user_status = active`

### 2-2. Products

| 항목 | 기대 기준값 | 점검 기준 | 실제 결과 | 판정 | 조치 |
|---|---|---|---|---|---|
| `products.product_status` | `on_sale`, `out_of_stock` | 상품 목록 응답에서 문서 기준 상태값으로 내려오는지 확인 |  |  |  |
| `products.is_active` | `true`, `false` | 비활성 상품이 목록/장바구니 담기 대상에서 배제되는지 확인 |  |  |  |

체크 메모:
- 상품 목록 조회 결과와 장바구니 담기 가능 조건이 동일해야 함
- `on_sale` 상품은 정상 구매 플로우에 사용 가능해야 함

### 2-3. Carts

| 항목 | 기대 기준값 | 점검 기준 | 실제 결과 | 판정 | 조치 |
|---|---|---|---|---|---|
| `carts.cart_status` | `active`, `checked_out` | 장바구니 생성 시 `active`, 주문 생성 후 `checked_out`로 전이되는지 확인 |  |  |  |

체크 메모:
- `POST /carts` 직후 `active`
- `POST /orders` 완료 후 해당 장바구니가 `checked_out` 처리되는지 확인

### 2-4. Orders

| 항목 | 기대 기준값 | 점검 기준 | 실제 결과 | 판정 | 조치 |
|---|---|---|---|---|---|
| `orders.order_status` | `created`, `paid`, `payment_failed` | 주문 생성 → 결제 성공/실패 후 상태 전이가 명세와 일치하는지 확인 |  |  |  |

체크 메모:
- 주문 생성 직후 `created`
- 결제 성공 시 `paid`
- 결제 실패 시 `payment_failed`

### 2-5. Coupons

| 항목 | 기대 기준값 | 점검 기준 | 실제 결과 | 판정 | 조치 |
|---|---|---|---|---|---|
| `coupons.coupon_status` | `active` | 체크아웃 진입 및 쿠폰 적용 시 활성 쿠폰만 노출되는지 확인 |  |  |  |

체크 메모:
- 현재 문서 기준 쿠폰 상태값은 `active`
- 유효기간 조건과 함께 동작하는지 확인

### 2-6. Payments

| 항목 | 기대 기준값 | 점검 기준 | 실제 결과 | 판정 | 조치 |
|---|---|---|---|---|---|
| `payments.payment_status` | `requested`, `paid`, `failed` | 결제 시뮬레이션 성공/실패 후 응답 및 주문 내역 조회 결과와 일치하는지 확인 |  |  |  |

체크 메모:
- 결제 성공 응답: `paid`
- 결제 실패 응답: `failed`
- 주문 내역 조회의 `payment_status`와 일치해야 함

### 2-7. Reviews

| 항목 | 기대 기준값 | 점검 기준 | 실제 결과 | 판정 | 조치 |
|---|---|---|---|---|---|
| `reviews.review_status` | `visible`, `deleted` | 리뷰 생성 시 `visible`, 리뷰 삭제 시 `deleted`로 전이되는지 확인 |  |  |  |

체크 메모:
- 리뷰 생성 성공 시 `visible`
- 리뷰 삭제는 물리 삭제가 아니라 soft delete여야 함

---

## 3. 에러 메시지 일관성 점검표

### 3-1. Not Found 계열

| 리소스 / 상황 | 기대 Status | 기대 Message | 실제 결과 | 판정 | 조치 |
|---|---:|---|---|---|---|
| User 없음 | `404` | `User not found` |  |  |  |
| Product 없음 | `404` | `Product not found` |  |  |  |
| Coupon 없음 | `404` | `Coupon not found` |  |  |  |
| Order 없음 | `404` | `Order not found` |  |  |  |
| Review 없음 | `404` | `Review not found` |  |  |  |
| Active cart 없음 | `404` | `Active cart not found` |  |  |  |
| Cart item 없음 | `404` | `Cart item not found` |  |  |  |
| Active session 없음 | `404` | `Active session not found` |  |  |  |

체크 메모:
- 리소스 없음 계열은 가능한 한 `X not found` 패턴으로 통일
- `Active cart not found`, `Active session not found`처럼 상태 조건이 붙는 경우만 예외적으로 구체 표현 유지

### 3-2. Conflict 계열

| 상황 | 기대 Status | 기대 Message | 실제 결과 | 판정 | 조치 |
|---|---:|---|---|---|---|
| 중복 회원가입 | `409` | `Email already exists` |  |  |  |
| 중복 리뷰 작성 | `409` | `Review already exists for this order item` |  |  |  |

체크 메모:
- 중복 생성/중복 등록 성격의 오류는 `409 Conflict` 유지 권장

### 3-3. Forbidden 계열

| 상황 | 기대 Status | 기대 Message | 실제 결과 | 판정 | 조치 |
|---|---:|---|---|---|---|
| 타인 리뷰 수정 | `403` | `You can only update your own review` |  |  |  |
| 타인 리뷰 삭제 | `403` | `You can only delete your own review` |  |  |  |

체크 메모:
- 권한 오류는 `You can only ...` 패턴으로 통일하는 것이 좋음

### 3-4. Bad Request 계열

| 상황 | 기대 Status | 기대 Message | 실제 결과 | 판정 | 조치 |
|---|---:|---|---|---|---|
| 빈 장바구니 체크아웃 | `400` | `Cart is empty` |  |  |  |
| 최소 주문금액 미달 쿠폰 | `400` | `Cart total does not meet coupon minimum order amount` |  |  |  |
| 결제 불가 주문 | `400` | `Order is not payable` |  |  |  |
| 구매 이력 없는 리뷰 | `400` | `Review can only be created for purchased products` |  |  |  |
| 삭제된 리뷰 수정 | `400` | `Deleted review cannot be updated` |  |  |  |
| 이미 삭제된 리뷰 삭제 | `400` | `Review is already deleted` |  |  |  |
| 미지원 쿠폰 타입 | `400` | `Unsupported coupon type` |  |  |  |

체크 메모:
- 상태 불일치, 도메인 규칙 위반, 사전조건 미충족은 `400 Bad Request` 유지
- 같은 성격인데 메시지 표현이 다른 항목이 있다면 통일 필요

### 3-5. Unauthorized 계열

| 상황 | 기대 Status | 기대 Message | 실제 결과 | 판정 | 조치 |
|---|---:|---|---|---|---|
| 로그인 실패 | `401` | `Invalid email or password` |  |  |  |

체크 메모:
- 인증 실패는 이메일/비밀번호를 구분하지 않는 현재 메시지 유지 권장

### 3-6. Internal Server Error 계열

| 상황 | 기대 Status | 기대 Message | 실제 결과 | 판정 | 조치 |
|---|---:|---|---|---|---|
| 사용자 생성 실패 | `500` | `Failed to create user` |  |  |  |
| 세션 생성 실패 | `500` | `Failed to create session` |  |  |  |
| 장바구니 생성 실패 | `500` | `Failed to create cart` |  |  |  |
| 장바구니 항목 추가 실패 | `500` | `Failed to add item to cart` |  |  |  |
| 장바구니 항목 수정 실패 | `500` | `Failed to update cart item` |  |  |  |
| 주문 생성 실패 | `500` | `Failed to create order` |  |  |  |
| 주문 항목 생성 실패 | `500` | `Failed to create order item` |  |  |  |
| 결제 생성 실패 | `500` | `Failed to create payment` |  |  |  |
| 리뷰 생성 실패 | `500` | `Failed to create review` |  |  |  |
| 리뷰 수정 실패 | `500` | `Failed to update review` |  |  |  |
| 리뷰 삭제 실패 | `500` | `Failed to delete review` |  |  |  |

체크 메모:
- 내부 처리 실패는 `Failed to ...` 패턴으로 유지하는 것이 가장 직관적
- 명세와 실제 메시지가 다르면 우선순위 높게 정리

---

## 4. 실제 검증 결과 반영용 종합 표

| 구분 | 항목 | 기대 결과 | 실제 결과 | 판정 | 조치 |
|---|---|---|---|---|---|
| 상태값 | 회원가입 후 `user_status` | `active` |  |  |  |
| 상태값 | 장바구니 생성 후 `cart_status` | `active` |  |  |  |
| 상태값 | 주문 생성 후 `order_status` | `created` |  |  |  |
| 상태값 | 결제 성공 후 `payment_status` | `paid` |  |  |  |
| 상태값 | 리뷰 생성 후 `review_status` | `visible` |  |  |  |
| 상태값 | 리뷰 삭제 후 `review_status` | `deleted` |  |  |  |
| 에러 | 중복 회원가입 | `409 / Email already exists` |  |  |  |
| 에러 | 빈 장바구니 체크아웃 | `400 / Cart is empty` |  |  |  |
| 에러 | 최소 주문금액 미달 쿠폰 | `400 / Cart total does not meet coupon minimum order amount` |  |  |  |
| 에러 | 결제 불가 주문 재결제 | `400 / Order is not payable` |  |  |  |
| 에러 | 구매 이력 없는 리뷰 | `400 / Review can only be created for purchased products` |  |  |  |
| 에러 | 중복 리뷰 작성 | `409 / Review already exists for this order item` |  |  |  |
| 에러 | 타인 리뷰 수정 | `403 / You can only update your own review` |  |  |  |
| 에러 | 타인 리뷰 삭제 | `403 / You can only delete your own review` |  |  |  |

---

## 5. 불일치 발생 시 조치 기준

### 5-1. 문서 수정 대상

아래 경우는 우선 문서 수정 대상으로 분류한다.

- 실제 API 응답은 합리적이지만 명세서 문구가 outdated 된 경우
- status code는 맞지만 example JSON이 낡은 경우
- 실제 응답 필드명은 맞고 문서만 누락된 경우

예:
- 문서에는 `201`이라고 적혀 있으나 실제 구현 의도상 `200`이 맞는 경우
- 설명 문구가 과거 상태값 이름을 유지하고 있는 경우

### 5-2. 코드 수정 대상

아래 경우는 코드 수정 대상으로 분류한다.

- 같은 유형의 오류인데 다른 status code가 내려오는 경우
- 같은 도메인 상태값이 API마다 다르게 표현되는 경우
- 응답 필드가 명세서와 다르고, 현재 프론트 연동에 혼선을 줄 수 있는 경우
- 에러 메시지가 지나치게 비일관적이거나 의미가 불명확한 경우

### 5-3. 후속 태스크 분리 대상

아래 경우는 D2C-53 종료 후 별도 태스크로 분리한다.

- 도메인 정책 자체를 다시 설계해야 하는 경우
- API 응답 계약을 광범위하게 바꿔야 하는 경우
- 미구현 / TBD 상태의 API를 추가 확정해야 하는 경우

예:
- `GET /products/{product_id}` 상세 응답 구조 확정
- `DELETE` 요청 body 사용 방식 재검토
- 인증/인가 구조 확장 필요성 검토

---

## 6. 최종 판정 섹션

### 6-1. 상태값 일관성 최종 판정

- [ ] 전 항목 이상 없음
- [ ] 일부 문서 수정 필요
- [ ] 일부 코드 수정 필요
- [ ] 후속 태스크 분리 필요

메모:

```text
- 
```

### 6-2. 에러 메시지 일관성 최종 판정

- [ ] 전 항목 이상 없음
- [ ] 일부 문서 수정 필요
- [ ] 일부 코드 수정 필요
- [ ] 후속 태스크 분리 필요

메모:

```text
- 
```

### 6-3. D2C-53 종료 여부

- [ ] 종료 가능
- [ ] 경미한 수정 후 종료 가능
- [ ] 후속 수정 완료 후 종료

메모:

```text
- 
```
