from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "local"
    app_port: int = 8000

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "d2c_commerce"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"

    database_url: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/d2c_commerce"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

settings = Settings()