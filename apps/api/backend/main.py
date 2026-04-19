from fastapi import FastAPI

from backend.api.routes.health import router as health_router
from backend.api.routes.categories import router as categories_router

app = FastAPI(title="D2C Commerce Prototype API")

app.include_router(health_router)
app.include_router(categories_router)

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}