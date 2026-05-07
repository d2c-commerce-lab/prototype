# D2C Commerce Prototype Functional Specification

## Document Purpose

> [!NOTE]
> This document is the reference document that defines the functional scope of the prototype and the criteria for data generation.  
> It serves as a common reference across implementation and overall data engineering design.

This document defines the functional scope and implementation criteria of the D2C commerce web prototype. This prototype is not intended to become a full production-grade commercial service. Its primary purpose is to recreate the kinds of user behaviors and business state changes that are likely to occur in a D2C commerce environment, and to reliably generate operational data and event logs in the process.

In other words, this document is not merely an application specification. It is a reference document that defines what kind of functional and data generation structure the source service must have in order to support subsequent work such as data pipeline construction, data quality validation, monitoring, and BI design. Accordingly, it serves as the starting point for frontend and backend implementation, database schema design, event log design, and subsequent data engineering work.

## The Service Model the Prototype Aims For

This prototype assumes a fictional D2C commerce platform that sells lifestyle and work-assistance products. The product categories are assumed to include desk setup accessories, productivity tools, office lifestyle goods, and small work-related items. This domain is appropriate because it naturally includes typical commerce behaviors such as product exploration, cart usage, ordering, coupon usage, and reviews, while avoiding excessive complexity at the prototype level.

Rather than prioritizing visual completeness or the complex exception handling expected in a production service, this service focuses on establishing a structure in which the core user flow can be completed end-to-end and the process is preserved as data. Accordingly, this prototype is closer to a service that generates analyzable data than to a polished service.

## Implementation Scope and Exclusions

> [!IMPORTANT]
> This implementation includes only the features directly required for the core purchase flow and data generation.  
> Additional features and advanced capabilities required for production operations are excluded from this scope.

The scope to be implemented in this prototype is clearly defined. Users must be able to enter the service through sign-up or login, browse categories and products from the home page, view product details, and add or remove items from the cart. They must then be able to move to the checkout stage, apply coupons, create orders, and simulate payment outcomes as either success or failure. Order history viewing and review writing for purchased products are also included in scope.

By contrast, real payment system integration, an admin page, sophisticated inventory management, complex SKU and option structures, recommendation systems, real-time notifications, advanced authorization models, customer support workflows, and production-grade deployment hardening are not included in this scope. While these elements may be meaningful from a product perspective, they are not core within the goals and timeline of this project. This document follows the principle of focusing on core flows that directly contribute to data generation, rather than expanding functionality indiscriminately.

## Core User Flow to Be Supported

The user flow that this prototype must support can be understood as follows. The user first signs up or logs in. The user then lands on the home page and browses products through categories or product listings. After viewing the details of a product of interest, the user adds it to the cart. On the cart page, the user must be able to review the current items and remove them if needed, then start checkout, apply a coupon, and create an order. Payment is handled by simulation rather than through integration with a real PG, and may result in either success or failure. After payment, the user must be able to view order history and, finally, write a review for the purchased product.

This user flow is not merely a sequence of page transitions. It is also the reference scenario for generating operational data and event logs. Accordingly, each step must be natural from the user’s perspective and traceable from a data perspective.

## Functional Implementation Criteria

Each function should be understood not only as a user-facing screen capability, but also as a unit that generates operational data and event logs. Accordingly, implementation should not stop at making the screen behavior work; it must also account for which tables are written to and which events are generated.

### User Authentication and Session Management

The user authentication function performs the basic roles of account creation and login. However, what is more important in this prototype is establishing the foundation for user identification and session tracking. Sign-up and login must be connected to the creation and update of the `users` table, and `sessions` data must be created when the user begins using the service.

Session management is required to reconstruct user behavior in sequence and to analyze how a given session leads from product views to adding items to the cart and then to orders. Therefore, the authentication function should not stop at basic account management; it must serve as the starting point for later funnel analysis and session-based conversion analysis.

### Product Discovery

The product discovery area captures user behavior before purchase intent is explicitly expressed. This area includes the home page, category browsing, product list viewing, and product detail viewing. These functions must do more than simply display screens; they must preserve the context of how the user reached a given product.

From the operational data perspective, this area is closely tied to `categories`, `products`, and `sessions`, and from the event perspective it must generate behavioral events such as `home_viewed`, `page_viewed`, `category_viewed`, and `product_viewed`. This area forms the basis for later analysis such as product-detail-to-cart conversion, category-level browsing performance, and behavioral differences by entry path.

### Cart Management

The cart function is the first stage in which browsing behavior transitions into purchase intent. Users must be able to create a cart, add products, remove products, and view the current state. This function directly affects the `carts` and `cart_items` tables, and must also generate the events `cart_viewed`, `cart_item_added`, and `cart_item_removed`.

The cart is a highly important signal in commerce analytics. Interpretation of which products a user showed interest in, when purchase intent emerged, and which products were frequently added and then removed begins with this data. Therefore, cart functionality should prioritize state management and data consistency over UI polish.

### Checkout, Order, and Payment

Checkout, order, and payment are the core business flow of this prototype. Users must be able to enter the checkout stage, review the products to be ordered, apply coupons when needed, and create orders. Payment is handled through simulation rather than connection to a real PG, but both success and failure must be preserved as state changes.

This process creates or updates data in the `coupons`, `orders`, `order_items`, and `payments` tables, and from the event perspective must generate `checkout_started`, `coupon_applied`, `order_created`, `payment_succeeded`, and `payment_failed`. In particular, even though payment is not a real financial transaction, order and payment states must still be clearly distinguished in data. This is necessary to enable later analysis such as payment success rate by order, payment failure patterns, and the relationship between coupon application and conversion.

### Review Writing

The review function handles post-purchase user behavior. Users must only be able to write reviews for products they have actually purchased, and this function is connected to `reviews`, `order_items`, `products`, and `users`. The event `review_created` must also be generated.

Although the review function is not the highest-priority function in the overall prototype, it is meaningful in that it preserves post-purchase behavior as data. This allows validation of post-purchase participation rate, review generation rate by product, and the linkage structure between ordered items and reviews.

## Page Design Principles

The screens provided by the prototype do not need to be complex, but they must be sufficient to support each functional flow. The home page should serve as the point where users first enter and begin browsing, and the login and sign-up pages should support authentication. The product list page should support category-based browsing and product selection, and the product detail page should provide basic information such as price, product name, brand, and an add-to-cart action.

The cart page should display the current items and lead into checkout, while the checkout page should handle review of the intended order, coupon application, order creation, and payment simulation. The order history page should allow users to view created orders and order statuses, and the review writing page should allow users to enter ratings and review text for purchased products.

These screens do not need to be visually elaborate, but the functional responsibility of each page must be clear.

## API Scope

The backend API must cover the minimum scope required to support the functional flow described above. In the authentication area, sign-up and login APIs are required. In product discovery, APIs for category retrieval, product list retrieval, and product detail retrieval are required. In cart management, APIs are required for cart creation, cart retrieval, and cart item addition and removal.

In the order and payment area, APIs are required for starting checkout, creating orders, simulating payment outcomes, and retrieving order history, while the review area requires an API for review creation. Paths and detailed naming may be adjusted during implementation, but functionally they must not go beyond this scope.

## Operational Data Generation Criteria

> [!IMPORTANT]
> The prototype must generate actual data in operational tables as a result of execution.  
> The basic principle is to manage seed data and runtime-generated data separately.

This prototype must generate actual operational data as a result of execution. The target tables are `users`, `sessions`, `categories`, `products`, `carts`, `cart_items`, `campaigns`, `coupons`, `orders`, `order_items`, `payments`, and `reviews`.

Among these, `categories`, `products`, `campaigns`, and `coupons` should be loaded as seed data during initial startup. In contrast, `users`, `sessions`, `carts`, `cart_items`, `orders`, `order_items`, `payments`, and `reviews` must be generated at runtime through actual user activity or test flows. This separation enables the service to establish an initial state quickly while still distinguishing it from dynamic, behavior-based data.

## Event Log Generation Criteria

> [!WARNING]
> If event logs are omitted, the core data engineering purpose of this project is undermined.  
> Operational records and event generation must be designed together within the same functional flow.

This prototype is not complete if it generates only operational data. User behavior and business state changes must also be preserved as events. User behavior events include home page views, page views, category views, product detail views, cart views, add-to-cart events, remove-from-cart events, checkout starts, coupon application, and review creation. Business state change events include order creation and payment success or failure.

Event generation is not an add-on to be attached after functional implementation. It is one of the original purposes of the prototype. Therefore, each function must handle operational recording and event generation within the same flow, and identifiers and timestamps must remain consistent so that operational data and event logs can later be cross-validated.

## Non-Functional Constraints and Implementation Principles

> [!CAUTION]
> Prioritizing UI polish or production-level complexity can quickly break the scope and schedule.  
> This prototype is focused on fast implementation and reliable data generation.

This prototype prioritizes completeness of the functional flow and the data generation structure. UI polish, production-grade exception handling, and advanced operational features are not priorities. Accordingly, implementation should be fast and simple, while the data must remain reliable.

Payment must be handled through simulation and must not integrate with an external payment system. This reduces development complexity while still recreating the important business states of payment success and failure. The development environment assumes Next.js and TypeScript for the frontend, FastAPI and Python for the backend, and PostgreSQL for the database, with Docker Compose used as the local environment standard.

## Priority Scope for Sprint 1

> [!TIP]
> Sprint 1 is best understood as the phase for establishing the foundation rather than completing the full product.  
> Stabilizing the data structure and core APIs first is more effective than polishing screens early.

Sprint 1 should focus on building the foundational structure rather than completing the full service. At this stage, the priority items are writing the functional specification, designing the frontend screen structure, drafting the operational DB schema DDL, designing seed data, setting up the backend, implementing sign-up and login APIs, implementing session creation and tracking logic, implementing category and product list/detail APIs, implementing cart creation/add/view APIs, and drafting the initial order creation API.

The purpose of this scope is to establish the foundation for later frontend integration, event log refinement, and end-to-end validation. Therefore, during Sprint 1, stability of the data structure and core APIs should take precedence over UI completeness.

## Expansion Direction After Sprint 1

Once the foundation is stable, frontend page implementation can proceed in earnest, and the checkout flow and payment simulation can be made more sophisticated. At this stage, it also becomes appropriate to begin connecting the review-writing function, refining the event generation structure, validating data consistency between operational data and event logs, and preparing for integration with the data pipeline.

Work after Sprint 1 should be understood less as adding entirely new capabilities and more as stably connecting the already defined functions and data flows to the user interface and logging structure.

## Completion Criteria

> [!IMPORTANT]
> The success criterion for this prototype is not the outward appearance of the service, but the reliability of the data-generating environment.  
> Completion is judged by consistent generation of operational and event data across the core flow.

This prototype is not considered successful when it looks like a polished commerce website. It is considered successful when users can sign up or log in, browse products, move through the cart, and create orders, while operational tables are populated consistently throughout the process and key user behavior events and order/payment state change events are generated. In addition, the resulting data must be usable as input for subsequent work such as data pipeline construction, quality validation, monitoring, and BI design.

Ultimately, the completion criterion defined by this document is not the appearance of the service, but whether a reliable data-generating environment has been established.