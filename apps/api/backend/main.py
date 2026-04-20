from fastapi import FastAPI

from backend.api.routes.auth import router as auth_router
from backend.api.routes.health import router as health_router
from backend.api.routes.categories import router as categories_router
from backend.api.routes.product_detail import router as product_detail_router
from backend.api.routes.products import router as products_router
from backend.api.routes.sessions import router as sessions_router


app = FastAPI(title="D2C Commerce Prototype API")

app.include_router(auth_router)
app.include_router(health_router)
app.include_router(categories_router)
app.include_router(products_router)
app.include_router(product_detail_router)
app.include_router(sessions_router)

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}