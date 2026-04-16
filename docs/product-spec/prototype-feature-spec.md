# D2C Commerce Prototype Feature Specification

> [!NOTE]
> This document defines the functional scope of the D2C commerce web prototype.  
> The prototype is not intended to be a production-grade commerce platform. Its primary goal is to generate realistic operational data and event logs that can later feed the data pipeline, data quality checks, observability layer, and BI dashboards.

---

## 1. Document Overview

### 1.1 Purpose

This document specifies the initial functional scope, user flows, system boundaries, and data generation goals for the D2C commerce prototype.

The prototype is designed to support two parallel objectives:

1. **Application-side objective**  
   Build a minimal but realistic commerce web application that supports core user actions such as browsing products, adding items to cart, placing orders, and writing reviews.

2. **Data-side objective**  
   Ensure that each core business action generates:
   - operational records in the source database
   - event logs representing user behavior and business state changes

In other words, this prototype is not just a web app. It is a **source data generator** for the broader data engineering project.

---

### 1.2 Scope

This specification covers the following areas:

- user-facing functional scope
- page scope
- API scope
- source-of-truth operational data generation
- event log generation boundaries
- explicit exclusions from the prototype

It serves as the baseline for:
- backend API implementation
- frontend screen design
- database schema implementation
- event schema implementation
- downstream pipeline planning

---

### 1.3 Prototype Goals

The prototype aims to achieve the following:

- reproduce the essential user journey of a D2C commerce platform
- generate realistic operational data in source tables
- generate user behavior events and order/payment status events
- provide a reliable source system for the future data platform
- support realistic internal stakeholder scenarios such as:
  - conversion analysis
  - cart abandonment analysis
  - coupon effectiveness analysis
  - payment failure investigation
  - review and post-purchase behavior analysis

> [!TIP]
> The prototype should prioritize **data-generating behavior** over visual completeness.  
> A simpler interface is acceptable as long as it reliably produces the right records and events.

---

## 2. Product Vision

### 2.1 Product Definition

The prototype represents a fictional **D2C lifestyle commerce platform** selling curated products such as:

- desk setup accessories
- productivity tools
- office lifestyle goods
- small personal work items

This domain was selected because it supports:
- natural browsing and category navigation
- cart and checkout behavior
- coupon and campaign use cases
- review creation after purchase
- manageable implementation scope for a prototype

---

### 2.2 Core User Journey

The system should allow a user to complete the following end-to-end journey:

1. Sign up or log in
2. Enter the home page
3. Browse categories or product listings
4. View a product detail page
5. Add an item to the cart
6. View and update the cart
7. Start checkout
8. Apply a coupon
9. Create an order
10. Simulate payment success or failure
11. View order history
12. Write a review for a purchased item

This journey defines the minimum viable behavior required to make the downstream data work meaningful.

---

## 3. Functional Scope

> [!IMPORTANT]
> Each functional area below must be evaluated not only from a UI perspective, but also from a **data generation perspective**.  
> For every major user action, the prototype should create both:
> - operational data in the application database
> - event data for analytics and monitoring

---

### 3.1 User Authentication and Session Management

#### Description

This functional area covers user identity creation and session tracking.  
It provides the foundation for user-based analytics, purchase attribution, and behavioral sequence reconstruction.

#### Included Features

- user sign-up
- user login
- session initialization and tracking

#### Expected Operational Data

- `users`
- `sessions`

#### Expected Events

- `user_signed_up`
- `user_logged_in`
- `session_started`

#### Notes

User identity and session tracking are critical because later analyses rely on them for:
- user-level funnel reconstruction
- repeat purchase calculation
- session-to-order attribution
- anonymous-to-authenticated behavior transition

> [!WARNING]
> Session creation must not be treated as optional.  
> Even in a lightweight prototype, session tracking is essential for later event pipeline design.

---

### 3.2 Product Discovery and Browsing

#### Description

This area covers how users explore the catalog before purchase intent becomes explicit.

#### Included Features

- home page access
- category browsing
- product listing access
- product detail view

#### Expected Operational Data

- `categories`
- `products`
- `sessions`

#### Expected Events

- `home_viewed`
- `page_viewed`
- `category_viewed`
- `product_viewed`

#### Notes

This area is important because it creates the upstream context for:
- conversion funnel analysis
- category performance analysis
- page-to-product interaction analysis
- product detail view vs. add-to-cart conversion analysis

The browsing layer should be simple, but it must still support distinct entry points such as:
- home page
- category page
- product list page
- product detail page

---

### 3.3 Cart Management

#### Description

This area captures the transition from browsing to purchase intent.

#### Included Features

- cart creation
- add item to cart
- remove item from cart
- view current cart state

#### Expected Operational Data

- `carts`
- `cart_items`

#### Expected Events

- `cart_viewed`
- `cart_item_added`
- `cart_item_removed`

#### Notes

Cart behavior is one of the most important behavioral signals in commerce systems.  
For the data engineering project, this area is essential because it supports:
- cart abandonment analysis
- product attractiveness analysis
- cart-to-checkout conversion analysis
- coupon targeting logic

> [!TIP]
> Even if cart functionality is simple, the app should preserve the cart state clearly enough that the backend can reflect it in source tables and later in marts.

---

### 3.4 Checkout, Order, and Payment

#### Description

This area captures the key business transition from purchase intent to business transaction.

#### Included Features

- checkout entry
- coupon application
- order creation
- payment success/failure simulation
- order history lookup

#### Expected Operational Data

- `coupons`
- `orders`
- `order_items`
- `payments`

#### Expected Events

- `checkout_started`
- `coupon_applied`
- `order_created`
- `payment_succeeded`
- `payment_failed`

#### Notes

This area is the business core of the prototype.

It must support:
- order creation in source tables
- payment state creation
- simulation of both successful and failed payments
- future investigation scenarios such as:
  - payment failure spikes
  - coupon impact on conversion
  - order volume monitoring
  - order-to-payment reconciliation

> [!IMPORTANT]
> Payment should be simulated, not integrated with a real payment gateway.  
> The objective is to produce realistic state transitions, not external payment correctness.

---

### 3.5 Review Creation

#### Description

This area covers post-purchase user engagement.

#### Included Features

- write a review for a purchased item

#### Expected Operational Data

- `reviews`
- `order_items`
- `products`
- `users`

#### Expected Events

- `review_created`

#### Notes

Review functionality is useful not because the prototype needs a rich review platform, but because it extends the lifecycle beyond purchase and supports:
- post-purchase engagement analysis
- review rate analysis
- product satisfaction proxy analysis
- join paths from order item to review

> [!NOTE]
> Reviews should be constrained to purchased items only, based on the ERD design linking reviews to `order_items`.

---

## 4. Page Scope

### 4.1 Home

#### Purpose
The home page acts as the main entry point to the platform.

#### Responsibilities
- present initial navigation
- provide access to categories or featured products
- serve as the initial event source for homepage traffic

#### Data Relevance
- generates homepage traffic events
- supports entry-point analysis

---

### 4.2 Login / Signup

#### Purpose
Allow users to create accounts and authenticate.

#### Responsibilities
- capture identity creation
- enable authenticated flows
- initialize sessions

#### Data Relevance
- supports user lifecycle analysis
- provides user_id for downstream joins

---

### 4.3 Product List

#### Purpose
Provide a browsable list of products by category or collection.

#### Responsibilities
- display products within a selected browsing context
- support click-through to product detail pages

#### Data Relevance
- supports product discovery analysis
- provides category-based behavioral context

---

### 4.4 Product Detail

#### Purpose
Allow the user to inspect a single product before purchase intent is expressed.

#### Responsibilities
- show product name, brand, and price
- allow add-to-cart action

#### Data Relevance
- serves as the key source for product detail views
- supports detail-view-to-cart conversion analysis

---

### 4.5 Cart

#### Purpose
Show the current purchase intent state.

#### Responsibilities
- display items currently in cart
- support item removal
- support transition into checkout

#### Data Relevance
- enables cart behavior analysis
- supports abandonment and conversion measurement

---

### 4.6 Checkout

#### Purpose
Represent the final decision stage before transaction completion.

#### Responsibilities
- show order candidate contents
- allow coupon application
- allow order creation
- trigger payment simulation

#### Data Relevance
- creates checkout events
- creates order and payment records
- supports transaction flow analysis

---

### 4.7 Orders

#### Purpose
Allow users to inspect past orders and their statuses.

#### Responsibilities
- show order list
- expose order-level state

#### Data Relevance
- supports order status checks
- provides UI-level visibility into business transaction outputs

---

### 4.8 Review Write

#### Purpose
Allow post-purchase review creation.

#### Responsibilities
- accept rating and review content
- associate review with a purchased order item

#### Data Relevance
- supports post-purchase engagement events
- supports review table population

---

## 5. API Scope

> [!TIP]
> The API list below defines the initial expected endpoints.  
> Naming and internal route structure may change during implementation, but the logical capability should remain.

---

### 5.1 Authentication APIs

- `POST /auth/signup`
- `POST /auth/login`

#### Purpose
Handle account creation and login.

---

### 5.2 Catalog APIs

- `GET /categories`
- `GET /products`
- `GET /products/{product_id}`

#### Purpose
Support browsing and product detail retrieval.

---

### 5.3 Cart APIs

- `POST /cart`
- `GET /cart`
- `POST /cart/items`
- `DELETE /cart/items/{cart_item_id}`

#### Purpose
Support cart creation and cart item management.

---

### 5.4 Checkout / Order / Payment APIs

- `POST /checkout`
- `POST /orders`
- `POST /payments/simulate`
- `GET /orders`

#### Purpose
Support purchase flow and payment simulation.

---

### 5.5 Review APIs

- `POST /reviews`

#### Purpose
Support review creation linked to a purchased item.

---

## 6. Operational Data Generation Scope

The prototype must generate records in the following source tables:

- `users`
- `sessions`
- `categories`
- `products`
- `carts`
- `cart_items`
- `campaigns`
- `coupons`
- `orders`
- `order_items`
- `payments`
- `reviews`

### Data Population Strategy

#### Seeded at initialization
- `categories`
- `products`
- `campaigns`
- `coupons`

#### Generated through user/system actions
- `users`
- `sessions`
- `carts`
- `cart_items`
- `orders`
- `order_items`
- `payments`
- `reviews`

> [!IMPORTANT]
> The prototype should not rely only on manual clicking to populate meaningful data.  
> A combination of seed data and runtime-generated data is necessary to support downstream analytics.

---

## 7. Event Log Generation Scope

### 7.1 User Behavior Events

The prototype should generate the following behavioral events:

- `home_viewed`
- `page_viewed`
- `category_viewed`
- `product_viewed`
- `cart_viewed`
- `cart_item_added`
- `cart_item_removed`
- `checkout_started`
- `coupon_applied`
- `review_created`

### 7.2 Business State Change Events

The prototype should generate the following business events:

- `order_created`
- `payment_succeeded`
- `payment_failed`

### 7.3 Event Generation Principles

- events should be emitted when meaningful user actions or business transitions occur
- event generation should align with the previously defined event schema draft
- operational writes and event generation should be handled within the same business flow
- timestamps and identifiers must be consistent enough for downstream joins and reconciliation

> [!WARNING]
> Event logging should not be treated as an afterthought added later.  
> It is one of the main objectives of the prototype itself.

---

## 8. Non-Functional Expectations

### 8.1 Implementation Level

The prototype is intentionally lightweight.

It should prioritize:
- end-to-end functionality
- reliable data generation
- traceable flows
- implementation speed

It does **not** need to prioritize:
- production-grade UI polish
- advanced authorization models
- sophisticated commerce edge cases

---

### 8.2 Payment Handling

The prototype will not integrate with a real payment gateway.

Instead:
- payment success and failure will be simulated
- payment records will still be generated
- downstream data use cases can still be validated

---

### 8.3 Development Environment

Planned local development stack:

- **Frontend**: Next.js + TypeScript
- **Backend**: FastAPI + Python
- **Database**: PostgreSQL
- **ORM / Migration**: SQLAlchemy + Alembic
- **Local environment**: Docker Compose

---

## 9. Explicit Exclusions

The following are intentionally out of scope for this prototype:

- real payment gateway integration
- admin dashboard
- advanced inventory logic
- complex product option / SKU management
- recommendation engine
- real-time notification system
- advanced role/permission management
- production deployment hardening
- customer support workflows

> [!NOTE]
> Excluding these features is intentional.  
> The goal is to preserve focus on the minimum set of commerce behaviors needed for realistic data generation.

---

## 10. Sprint 1 Priority Scope

Sprint 1 should focus on the foundational application and data setup required to make the prototype executable.

### Sprint 1 priorities
- feature specification completion
- frontend screen structure design
- operational DB schema DDL draft
- seed data design
- backend bootstrap
- signup/login APIs
- session creation and tracking logic
- category/product list and detail APIs
- cart creation / add / view APIs
- initial order creation API

> [!TIP]
> Sprint 1 should favor backend and data foundations over UI completeness.

---

## 11. Post-Sprint 1 Expansion Scope

After the initial foundation is complete, the prototype can be extended with:

- frontend page implementation
- richer checkout flow behavior
- payment simulation refinement
- review flow integration
- event logging refinement
- source-to-event reconciliation checks
- pipeline integration readiness work

---

## 12. Success Criteria

The prototype can be considered successful when:

- a user can move from sign-up or login to order creation
- source tables are populated consistently
- key user behavior events are emitted
- key business state events are emitted
- the resulting data is sufficient to support the next data engineering phases

> [!SUCCESS]
> The prototype succeeds not when it looks like a finished commerce service,  
> but when it creates a reliable and analyzable data-generating environment.