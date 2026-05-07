from fastapi import FastAPI

from backend.api.routes.auth import router as auth_router
from backend.api.routes.cart_items import router as cart_items_router
from backend.api.routes.carts import router as carts_router
from backend.api.routes.categories import router as categories_router
from backend.api.routes.checkout import router as checkout_router
from backend.api.routes.coupon_apply import router as coupon_apply_router
from backend.api.routes.health import router as health_router
from backend.api.routes.order_history import router as order_history_router
from backend.api.routes.orders import router as orders_router
from backend.api.routes.payments import router as payments_router
from backend.api.routes.product_detail import router as product_detail_router
from backend.api.routes.products import router as products_router
from backend.api.routes.reviews import router as reviews_router
from backend.api.routes.sessions import router as sessions_router

app = FastAPI(title="D2C Commerce Prototype API")

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(products_router)
app.include_router(product_detail_router)
app.include_router(sessions_router)
app.include_router(carts_router)
app.include_router(cart_items_router)
app.include_router(checkout_router)
app.include_router(coupon_apply_router)
app.include_router(orders_router)
app.include_router(order_history_router)
app.include_router(payments_router)
app.include_router(reviews_router)

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}