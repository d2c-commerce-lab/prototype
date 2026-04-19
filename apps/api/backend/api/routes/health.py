from fastapi import APIRouter

from backend.db.connection import check_db_connection

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, object]:
    db_ok = False

    try:
        db_ok = check_db_connection()
    except Exception:
        db_ok = False

    return {
        "status": "ok",
        "database": "connected" if db_ok else "disconnected",
    }
