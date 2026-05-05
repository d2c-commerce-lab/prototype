---
title: Backend Run and Test Guide
version: v1.0
language: en
domain: backend
doc_type: operations-guide
---

# Backend Run and Test Guide

## 0. Purpose

This document defines the procedure for running the D2C Commerce Prototype backend **in a local environment, executing tests, and reproducing the core user flow in a repeatable way**.

The goals of this document are:

- standardize the execution procedure so the development environment can be reproduced quickly
- connect unit testing and manual validation in a single operational guide
- reorganize the API specification and user-flow validation results from D2C-53 from an execution perspective
- establish a clear backend-only baseline before frontend integration

---

## 1. Scope

This document includes the following scope.

- Python virtual environment setup
- dependency installation
- Docker / PostgreSQL preparation
- schema synchronization checks
- **seed data loading**
- backend server startup
- unit test execution
- manual validation of core APIs
- result logging and checklist usage
- representative error handling

The validation scope for the core user flow covers sign-up, login, session, catalog, cart, checkout, coupon, order, payment, and review flows.

---

## 2. Prerequisites

### 2-1. Required Tools

- Python 3.12 series
- Docker Desktop
- environment capable of running a PostgreSQL container
- PowerShell or terminal
- optional: Postman / Swagger UI

### 2-2. Project Preparation

Check the backend working location from the project root.

Example base URL:

```text
http://localhost:8000
```

### 2-3. Data Preparation

The following seed or initial data should be ready.

- `categories`
- `campaigns`
- `products`
- `coupons`
- at least one active product eligible for order creation
- at least one valid coupon in `active` state

### 2-4. Recommended Companion Outputs

This guide should be used together with the following documents.

- finalized API specification
- manual validation scenario for the core user flow
- state / error message consistency checklist

---

## 3. Local Environment Execution Procedure

### Step 1. Create Virtual Environment

```bash
python -m venv .venv
```

### Step 2. Activate Virtual Environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

### Step 3. Install Dependencies

Example for a `requirements.txt`-based project:

```bash
pip install -r requirements.txt
```

If the project uses `pyproject.toml`:

```bash
pip install -e .
```

### Step 4. Check Environment Variables

Verify that DB connection information and app settings are correctly defined in `.env` or the settings file.

Example items to check:

- DB host
- DB port
- DB name
- DB user
- DB password
- app env
- debug option

---

## 4. DB / Docker Preparation Procedure

### Step 1. Verify PostgreSQL Container Status

```bash
docker ps
```

### Step 2. Verify DB Connection

```bash
docker exec -it d2c-postgres psql -U postgres -d d2c_commerce
```

### Step 3. Verify Major Tables Exist

```bash
docker exec -it d2c-postgres psql -U postgres -d d2c_commerce -c "\dt"
```

### Step 4. Inspect Core Table Schemas

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

### Step 5. Check Schema Synchronization

- verify that `schema.sql` matches the local Docker DB structure
- verify that recent ALTER changes are reflected
- verify that seed data is already present where expected

### Step 6. Load Seed Data

The current project uses `scripts/seed/load_seed.ps1` to apply the seed SQL files in sequence.

#### 6-1. Actual Seed Files Applied

According to `load_seed.ps1`, the files are applied in the following order.

1. `seed_categories.sql`
2. `seed_campaigns.sql`
3. `seed_products.sql`
4. `seed_coupons.sql`

This order reflects the reference dependency flow of category → campaign → product → coupon.

#### 6-2. What the Script Does

`load_seed.ps1` performs the following steps.

- verifies that the `docker` command exists
- verifies that the target container is running
- verifies that each seed SQL file exists
- pipes each SQL file into `docker exec -i ... psql` sequentially
- stops immediately if any step fails
- prints `"All seed files applied successfully."` when all files are applied successfully

The script also uses the following default values.

- `CONTAINER_NAME`: `d2c-postgres`
- `DB_NAME`: `d2c_commerce`
- `DB_USER`: `postgres`

#### 6-3. Expected Seed Directory

The script path is assumed to be:

```text
scripts/seed/load_seed.ps1
```

From that location, the seed directory is resolved as:

```text
db/seeds
```

That means the following files should exist in the repository.

- `db/seeds/seed_categories.sql`
- `db/seeds/seed_campaigns.sql`
- `db/seeds/seed_products.sql`
- `db/seeds/seed_coupons.sql`

#### 6-4. PowerShell Execution Example

Run it from the project root like this:

```powershell
.\scripts\seed\load_seed.ps1
```

Or execute it explicitly by file path:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\seed\load_seed.ps1
```

#### 6-5. Environment Variable Override Example

If the container name, database name, or DB user differ from the defaults, set them in the current PowerShell session before running the script.

```powershell
$env:CONTAINER_NAME = "d2c-postgres"
$env:DB_NAME = "d2c_commerce"
$env:DB_USER = "postgres"

.\scripts\seed\load_seed.ps1
```

#### 6-6. Post-Load Verification

After loading, verify row counts like this.

```bash
docker exec -it d2c-postgres psql -U postgres -d d2c_commerce -c "SELECT COUNT(*) FROM categories;"
docker exec -it d2c-postgres psql -U postgres -d d2c_commerce -c "SELECT COUNT(*) FROM campaigns;"
docker exec -it d2c-postgres psql -U postgres -d d2c_commerce -c "SELECT COUNT(*) FROM products;"
docker exec -it d2c-postgres psql -U postgres -d d2c_commerce -c "SELECT COUNT(*) FROM coupons;"
```

#### 6-7. Seed Verification Criteria

- `categories` data exists
- `campaigns` data exists
- `products` data exists
- `coupons` data exists
- active coupons such as `WELCOME10` and `DESK5000` can be verified
- products such as `Laptop Stand Lite` can be used in order/review validation

#### 6-8. Seed Data Notes

Based on the uploaded seed SQL files, the dataset has the following characteristics.

- 6 category rows are inserted
- campaign rows are inserted
- multiple product rows are inserted
- coupon statuses include `active`, `expired`, and `inactive`
- for manual validation, using an `active` coupon such as `WELCOME10` is appropriate

---

## 5. Backend Server Startup Procedure

### Step 1. Start the Server

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 2. Verify Server Access

In a browser or terminal, verify the following.

- `http://localhost:8000`
- `http://localhost:8000/docs`

### Step 3. Verify Swagger UI

Check that the major endpoint groups are registered in Swagger UI.

Recommended scope:

- Auth
- Session
- Catalog
- Cart
- Checkout / Coupon
- Order / Payment
- Review

---

## 6. Basic Smoke Check Procedure

Immediately after the server starts, verify at least the following.

### Step 1. Check Representative GET APIs

```powershell
Invoke-RestMethod -Method Get -Uri "http://localhost:8000/categories"
Invoke-RestMethod -Method Get -Uri "http://localhost:8000/products"
```

### Step 2. Check Representative POST APIs

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

### Step 3. Verify Response Structure

Quickly check the following items.

- status code
- whether the JSON body is parseable
- whether key identifiers are returned
- whether errors use the `detail` structure

---

## 7. Test Execution Procedure

### 7-1. Run an Individual Test

Example:

```bash
python -m pytest .\tests\test_signup.py -v
```

### 7-2. Run the Full Test Suite

```bash
python -m pytest .\tests -v
```

### 7-3. Recommended Execution Order

- right after implementing a feature: run the related test file first
- after integrating multiple features: run the full test suite
- right before documentation freeze: re-run representative tests

### 7-4. Example Test Result Log

```md
## [Test Result] test_signup.py
- Command: python -m pytest .\tests\test_signup.py -v
- Result: Passed / Failed
- Notes:
  - error message:
  - whether a fix was applied:
```

---

## 8. Manual Validation Procedure for the Core User Flow

This stage should be executed based on the separately prepared **manual validation scenario document for the core user flow**.

Recommended order for the normal flow:

1. sign up
2. login
3. start session
4. get categories
5. get product list
6. create cart
7. add item to cart
8. get cart detail
9. enter checkout
10. apply coupon
11. create order
12. simulate successful payment
13. get order history
14. create review
15. update review
16. delete review
17. end session

Recommended order for the exception flow:

1. duplicate sign-up
2. empty cart checkout
3. coupon minimum order amount not met
4. retry payment on a non-payable order
5. create review without purchase history
6. create duplicate review
7. update/delete another user’s review

### Example Shared PowerShell Variables

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

### Example Manual Validation Log

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
- Verdict: Pass / Fail
- Notes:
  - whether it matches the specification
  - whether required fields are missing
```

---

## 9. Result Logging Method

### 9-1. Test Result Logging

Items to record:

- executed command
- target test file
- pass / fail result
- error message
- action taken

### 9-2. Manual Validation Result Logging

Items to record:

- step number
- endpoint / method
- request body or query parameter
- expected result
- actual result
- verdict
- notes

### 9-3. Reflect Results into the Consistency Checklists

After manual validation is complete, the following documents must be updated.

- state value consistency checklist
- error message consistency checklist

---

## 10. Common Issues and Responses

### 10-1. The Server Starts but DB Errors Occur

Check the following:

- whether the Docker container is running
- DB host / port / name / user / password
- `.env` settings
- whether the schema has been applied

### 10-2. `404 Not Found` Appears Unexpectedly

Check the following:

- whether the latest identifier from the previous step is being used
- whether a resource with an active-state condition is being reused incorrectly

Examples:
- `Active cart not found`
- `Active session not found`

### 10-3. The Cart / Order Flow Is Blocked

Check the following:

- whether the cart is not empty
- whether the product is active
- whether the coupon minimum order amount is satisfied
- whether the cart is already in `checked_out` state

### 10-4. Payment Simulation Fails

Check the following:

- whether the order state is `created` or `payment_failed`
- whether an already `paid` order is being retried

### 10-5. Review Create / Update / Delete Fails

Check the following:

- whether `order_item_id` belongs to a completed purchase
- whether a review already exists for the same `order_item_id`
- whether update/delete is being attempted with another user’s `user_id`
- whether the review is already in `deleted` state

### 10-6. Seed Loading Fails

Check the following:

- whether the `docker` command is available in PowerShell
- whether the `d2c-postgres` container is actually running
- whether all four seed SQL files exist under `db/seeds`
- whether prerequisite tables such as `campaigns` and `categories` already exist
- whether `scripts/seed/load_seed.ps1` is being executed from the project-root context

Representative failure messages include:

- `docker command not found.`
- `Container 'd2c-postgres' is not running.`
- `Seed file not found: ...`
- `Failed to apply seed_products.sql`

### 10-7. The Document and Actual Response Differ

Classify the issue in the following order.

1. check whether the document example is outdated
2. check whether the implementation differs from the intended design
3. reflect the issue in the state / error consistency checklist
4. split it into a follow-up task if needed

### 10-8. Gap Around Product Detail Retrieval

If `GET /products/{product_id}` is still pending finalization, keep it as an **optional verification item** in this document.

---

## 11. Final Checklist

### Execution Check

- [ ] virtual environment created
- [ ] virtual environment activated
- [ ] dependencies installed
- [ ] Docker/PostgreSQL verified
- [ ] core tables verified
- [ ] seed data loaded
- [ ] backend server started
- [ ] `/docs` accessible

### Testing Check

- [ ] key unit tests executed
- [ ] full test suite executed
- [ ] failed-test causes recorded

### Manual Validation Check

- [ ] normal flow A-1 ~ A-17 completed
- [ ] exception flow B-1 ~ B-7 completed
- [ ] actual API call results recorded

### Documentation Check

- [ ] API specification compared against actual responses
- [ ] state / error message checklist updated
- [ ] follow-up fixes separated where needed
