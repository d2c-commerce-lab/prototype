---
title: 백엔드 실행 및 테스트 가이드
version: v1.0
language: ko
domain: backend
doc_type: operations-guide
---

# 백엔드 실행·테스트 절차

## 0. 문서 목적

본 문서는 D2C Commerce Prototype 백엔드를 **로컬 환경에서 실행하고, 테스트하며, 핵심 사용자 흐름을 재현 가능한 방식으로 검증하기 위한 절차**를 정리한 문서다.

본 문서의 목적은 아래와 같다.

- 개발 환경을 빠르게 재현할 수 있도록 실행 절차를 표준화
- 단위 테스트와 수동 검증 절차를 한 문서에서 연결
- D2C-53에서 정리한 API 명세와 사용자 흐름 검증 결과를 실제 실행 관점에서 다시 사용할 수 있도록 정리
- 프론트엔드 연동 전에 백엔드 단독 실행 기준을 명확히 확보

---

## 1. 문서 범위

본 문서는 아래 범위를 포함한다.

- Python 가상환경 준비
- 의존성 설치
- Docker/PostgreSQL 준비
- 스키마 반영 여부 확인
- **seed 데이터 적재**
- 백엔드 서버 실행
- 단위 테스트 실행
- 핵심 API 수동 검증
- 결과 기록 및 체크리스트
- 대표적인 오류 대응

핵심 사용자 흐름 검증 범위는 회원가입, 로그인, 세션, 카탈로그, 장바구니, 체크아웃, 쿠폰, 주문, 결제, 리뷰까지다.

---

## 2. 사전 준비 사항

### 2-1. 필수 도구

- Python 3.12 계열
- Docker Desktop
- PostgreSQL 컨테이너 실행 가능 환경
- PowerShell 또는 터미널
- 선택: Postman / Swagger UI

### 2-2. 프로젝트 준비

프로젝트 루트에서 백엔드 디렉터리 기준 위치를 확인한다.

기본 Base URL 예시:

```text
http://localhost:8000
```

### 2-3. 데이터 준비

아래 seed 또는 초기 데이터가 준비되어 있어야 한다.

- `categories`
- `campaigns`
- `products`
- `coupons`
- 주문 생성 가능한 활성 상품
- 유효한 `active` 쿠폰

### 2-4. 권장 산출물 연결

본 문서는 아래 문서들과 함께 사용한다.

- API 명세서 최종본
- 핵심 사용자 흐름 수동 검증 시나리오 문서
- 상태값 / 에러 메시지 일관성 점검표

---

## 3. 로컬 환경 실행 절차

### Step 1. 가상환경 생성

```bash
python -m venv .venv
```

### Step 2. 가상환경 활성화

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

### Step 3. 의존성 설치

`requirements.txt` 기반 예시:

```bash
pip install -r requirements.txt
```

프로젝트가 `pyproject.toml` 기반이면:

```bash
pip install -e .
```

### Step 4. 환경 변수 확인

DB 접속 정보, 앱 설정 정보가 `.env` 또는 설정 파일에 맞게 들어 있는지 확인한다.

예시 확인 항목:

- DB host
- DB port
- DB name
- DB user
- DB password
- app env
- debug 옵션

---

## 4. DB / Docker 준비 절차

### Step 1. PostgreSQL 컨테이너 실행 확인

```bash
docker ps
```

### Step 2. 대상 DB 접속 확인

```bash
docker exec -it d2c-postgres psql -U postgres -d d2c_commerce
```

### Step 3. 주요 테이블 존재 확인

```bash
docker exec -it d2c-postgres psql -U postgres -d d2c_commerce -c "\dt"
```

### Step 4. 핵심 테이블 스키마 점검

```bash
docker exec -it d2c-postgres psql -U postgres -d d2c_commerce -c "\d users"
docker exec -it d2c-postgres psql -U postgres -d d2c_commerce -c "\d sessions"
docker exec -it d2c-postgres psql -U postgres -d d2c_commerce -c "\d categories"
docker exec -it d2c-postgres psql -U postgres -d d2c_commerce -c "\d campaigns"
docker exec -it d2c-postgres psql -U postgres -d d2c_commerce -c "\d products"
docker exec -it d2c-postgres psql -U postgres -d d2c_commerce -c "\d carts"
docker exec -it d2c-postgres psql -U postgres -d d2c_commerce -c "\d cart_items"
docker exec -it d2c-postgres psql -U postgres -d d2c_commerce -c "\d coupons"
docker exec -it d2c-postgres psql -U postgres -d d2c_commerce -c "\d orders"
docker exec -it d2c-postgres psql -U postgres -d d2c_commerce -c "\d order_items"
docker exec -it d2c-postgres psql -U postgres -d d2c_commerce -c "\d payments"
docker exec -it d2c-postgres psql -U postgres -d d2c_commerce -c "\d reviews"
```

### Step 5. 스키마 반영 여부 점검

- `schema.sql`과 local docker DB 구조가 일치하는지 확인
- 최근 ALTER 반영 여부 확인
- seed 데이터가 실제로 들어 있는지 확인

### Step 6. seed 데이터 적재

현재 프로젝트는 `scripts/seed/load_seed.ps1` 스크립트를 통해 seed SQL 파일들을 순차 적용하는 방식으로 구성되어 있다.

#### 6-1. 실제 적재 대상 파일

`load_seed.ps1` 기준 적용 순서는 아래와 같다.

1. `seed_categories.sql`
2. `seed_campaigns.sql`
3. `seed_products.sql`
4. `seed_coupons.sql`

이 순서는 카테고리 → 캠페인 → 상품 → 쿠폰의 참조 관계를 고려한 순서다.

#### 6-2. 스크립트 동작 방식

`load_seed.ps1`는 아래를 수행한다.

- `docker` 명령 존재 여부 확인
- 대상 컨테이너 실행 여부 확인
- 각 seed SQL 파일 존재 여부 확인
- 각 SQL 파일을 `docker exec -i ... psql`로 순차 반영
- 중간 실패 시 즉시 종료
- 모두 성공하면 `"All seed files applied successfully."` 출력

또한 스크립트 기본값은 아래와 같다.

- `CONTAINER_NAME`: `d2c-postgres`
- `DB_NAME`: `d2c_commerce`
- `DB_USER`: `postgres`

#### 6-3. seed 파일 위치 기준

스크립트 경로가 아래와 같다고 가정한다.

```text
scripts/seed/load_seed.ps1
```

이 기준에서 스크립트가 참조하는 seed 파일 디렉터리는 아래로 계산된다.

```text
db/seeds
```

즉, 레포 기준으로 아래 파일들이 존재해야 한다.

- `db/seeds/seed_categories.sql`
- `db/seeds/seed_campaigns.sql`
- `db/seeds/seed_products.sql`
- `db/seeds/seed_coupons.sql`

#### 6-4. PowerShell 실행 예시

프로젝트 루트에서 실행:

```powershell
.\scripts\seed\load_seed.ps1
```

또는 명시적으로 실행:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\seed\load_seed.ps1
```

#### 6-5. 환경 변수 오버라이드 예시

기본 컨테이너명/DB명/DB유저가 다르면 PowerShell 세션에서 아래처럼 지정 후 실행할 수 있다.

```powershell
$env:CONTAINER_NAME = "d2c-postgres"
$env:DB_NAME = "d2c_commerce"
$env:DB_USER = "postgres"

.\scripts\seed\load_seed.ps1
```

#### 6-6. 적재 완료 확인

적재 후에는 아래처럼 건수 확인을 수행한다.

```bash
docker exec -it d2c-postgres psql -U postgres -d d2c_commerce -c "SELECT COUNT(*) FROM categories;"
docker exec -it d2c-postgres psql -U postgres -d d2c_commerce -c "SELECT COUNT(*) FROM campaigns;"
docker exec -it d2c-postgres psql -U postgres -d d2c_commerce -c "SELECT COUNT(*) FROM products;"
docker exec -it d2c-postgres psql -U postgres -d d2c_commerce -c "SELECT COUNT(*) FROM coupons;"
```

#### 6-7. 적재 확인 기준

- `categories` 데이터 존재
- `campaigns` 데이터 존재
- `products` 데이터 존재
- `coupons` 데이터 존재
- `WELCOME10`, `DESK5000` 같은 활성 쿠폰 확인 가능
- `Laptop Stand Lite` 등 주문/리뷰 검증에 사용할 상품 확인 가능

#### 6-8. seed 데이터 특이사항

업로드된 seed SQL 기준으로 다음 특성이 있다.

- 카테고리 6건 적재
- 캠페인 데이터 적재
- 상품 다건 적재
- 쿠폰 상태값은 `active`, `expired`, `inactive`가 혼재
- 수동 검증에는 `WELCOME10` 같은 `active` 쿠폰을 사용하는 것이 적절

---

## 5. 백엔드 서버 실행 절차

### Step 1. 서버 실행

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 2. 서버 접속 확인

브라우저 또는 터미널에서 아래를 확인한다.

- `http://localhost:8000`
- `http://localhost:8000/docs`

### Step 3. Swagger UI 확인

Swagger UI에서 등록된 주요 엔드포인트를 확인한다.

권장 확인 범위:

- 인증(Auth)
- 세션(Session)
- 카탈로그(Catalog)
- 장바구니(Cart)
- 체크아웃 / 쿠폰
- 주문 / 결제
- 리뷰(Review)

---

## 6. 기본 동작 확인 절차

서버 실행 직후 최소 아래를 확인한다.

### Step 1. 대표 GET API 확인

```powershell
Invoke-RestMethod -Method Get -Uri "http://localhost:8000/categories"
Invoke-RestMethod -Method Get -Uri "http://localhost:8000/products"
```

### Step 2. 대표 POST API 확인

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:8000/auth/signup" `
  -ContentType "application/json" `
  -Body '{"email":"smokecheck_user@example.com","user_name":"smokecheck-user","password":"Password123!","marketing_opt_in_yn":true}'
```

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:8000/auth/login" `
  -ContentType "application/json" `
  -Body '{"email":"smokecheck_user@example.com","password":"Password123!"}'
```

### Step 3. 응답 구조 확인

아래 항목을 빠르게 점검한다.

- status code
- JSON body 파싱 가능 여부
- 주요 식별자 반환 여부
- 에러 발생 시 `detail` 구조 사용 여부

---

## 7. 테스트 실행 절차

### 7-1. 개별 테스트 실행

예시:

```bash
python -m pytest .\tests\test_signup.py -v
```

### 7-2. 전체 테스트 실행

```bash
python -m pytest .\tests -v
```

### 7-3. 권장 실행 순서

- 기능 구현 직후: 관련 테스트 파일 우선 실행
- 여러 기능 병합 후: 전체 테스트 실행
- 문서화 직전: 대표 테스트 재실행

### 7-4. 테스트 결과 기록 예시

```md
## [테스트 결과] test_signup.py
- 명령어: python -m pytest .\tests\test_signup.py -v
- 결과: Passed / Failed
- 비고:
  - 오류 메시지:
  - 수정 여부:
```

---

## 8. 핵심 사용자 흐름 수동 검증 절차

이 단계는 별도 작성한 **핵심 사용자 흐름 수동 검증 시나리오 문서**를 기준으로 진행한다.

정상 흐름 권장 순서:

1. 회원가입
2. 로그인
3. 세션 시작
4. 카테고리 조회
5. 상품 목록 조회
6. 장바구니 생성
7. 장바구니 담기
8. 장바구니 조회
9. 체크아웃 진입
10. 쿠폰 적용
11. 주문 생성
12. 결제 성공 시뮬레이션
13. 주문 내역 조회
14. 리뷰 생성
15. 리뷰 수정
16. 리뷰 삭제
17. 세션 종료

예외 흐름 권장 순서:

1. 중복 회원가입
2. 빈 장바구니 체크아웃
3. 최소 주문금액 미달 쿠폰 적용
4. 결제 불가 상태 주문 재결제
5. 구매 이력 없는 리뷰 작성
6. 중복 리뷰 작성
7. 타인 리뷰 수정/삭제

### PowerShell 공통 변수 선언 예시

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

### 수동 검증 기록 예시

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

## 9. 결과 기록 방식

### 9-1. 테스트 결과 기록

기록 항목:

- 실행 명령어
- 대상 테스트 파일
- 통과/실패 여부
- 오류 메시지
- 조치 여부

### 9-2. 수동 검증 결과 기록

기록 항목:

- Step 번호
- endpoint / method
- 요청 body 또는 query param
- 기대 결과
- 실제 결과
- 판정
- 비고

### 9-3. 일관성 점검표 반영

수동 검증이 끝난 뒤에는 반드시 아래 문서에 결과를 반영한다.

- 상태값 일관성 점검표
- 에러 메시지 일관성 점검표

---

## 10. 자주 발생하는 오류와 대응

### 10-1. 서버는 실행됐지만 DB 오류가 나는 경우

확인할 것:

- Docker 컨테이너 실행 여부
- DB host / port / name / user / password
- `.env` 설정
- schema 반영 여부

### 10-2. `404 Not Found`가 예상과 다르게 나오는 경우

확인할 것:

- 이전 단계에서 받은 최신 식별자를 사용했는지
- 상태 조건이 붙은 리소스를 잘못 재사용하고 있지 않은지

예:
- `Active cart not found`
- `Active session not found`

### 10-3. 장바구니 / 주문 흐름이 막히는 경우

확인할 것:

- 장바구니가 비어 있지 않은지
- 상품이 활성 상태인지
- 쿠폰 최소 주문금액을 충족하는지
- 장바구니가 이미 `checked_out` 상태가 아닌지

### 10-4. 결제 시뮬레이션이 실패하는 경우

확인할 것:

- 주문 상태가 `created` 또는 `payment_failed`인지
- 이미 `paid` 상태의 주문을 재결제하려 하고 있지 않은지

### 10-5. 리뷰 작성/수정/삭제가 실패하는 경우

확인할 것:

- `order_item_id`가 실제 구매 완료 주문의 항목인지
- 동일 `order_item_id`로 이미 리뷰가 존재하는지
- 다른 사용자 `user_id`로 수정/삭제를 시도하는지
- 이미 `deleted` 상태의 리뷰인지

### 10-6. seed 적재가 실패하는 경우

확인할 것:

- `docker` 명령이 PowerShell에서 사용 가능한지
- `d2c-postgres` 컨테이너가 실제로 실행 중인지
- `db/seeds` 디렉터리에 4개 seed SQL 파일이 모두 존재하는지
- `campaigns`, `categories` 등 선행 테이블이 이미 생성되어 있는지
- 프로젝트 루트 기준에서 `scripts/seed/load_seed.ps1`를 실행하고 있는지

대표 실패 메시지 예:

- `docker command not found.`
- `Container 'd2c-postgres' is not running.`
- `Seed file not found: ...`
- `Failed to apply seed_products.sql`

### 10-7. 문서와 실제 응답이 다른 경우

아래 순서로 분류한다.

1. 문서 예시가 낡았는지 확인
2. 코드가 실제 의도와 다르게 구현됐는지 확인
3. 상태값 / 에러 메시지 일관성 점검표에 반영
4. 필요 시 후속 태스크로 분리

### 10-8. 상품 상세 조회 관련 공백

`GET /products/{product_id}`는 별도 최종 확정 전 항목이라면, 본 문서에서는 **선택 확인 항목**으로 남긴다.

---

## 11. 최종 체크리스트

### 실행 체크

- [ ] 가상환경 생성 완료
- [ ] 가상환경 활성화 완료
- [ ] 의존성 설치 완료
- [ ] Docker/PostgreSQL 실행 확인 완료
- [ ] 주요 테이블 확인 완료
- [ ] seed 데이터 적재 완료
- [ ] 백엔드 서버 실행 완료
- [ ] `/docs` 접근 확인 완료

### 테스트 체크

- [ ] 핵심 단위 테스트 실행 완료
- [ ] 전체 테스트 실행 완료
- [ ] 실패 테스트 원인 기록 완료

### 수동 검증 체크

- [ ] 정상 흐름 A-1 ~ A-17 완료
- [ ] 예외 흐름 B-1 ~ B-7 완료
- [ ] 실제 호출 결과 기록 완료

### 문서 체크

- [ ] API 명세서와 실제 응답 대조 완료
- [ ] 상태값 / 에러 메시지 점검표 반영 완료
- [ ] 후속 수정 필요 사항 분리 완료
