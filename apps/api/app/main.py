from fastapi import FastAPI

app = FastAPI(title="D2C Commerce Prototype API")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}