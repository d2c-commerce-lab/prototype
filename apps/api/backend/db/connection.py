from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from backend.core.config import settings

engine: Engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

def check_db_connection() -> bool:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return result.scalar() == 1