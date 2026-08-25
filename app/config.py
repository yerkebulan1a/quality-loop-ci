import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://qa_user:qa_password@postgres:5432/qa_db"
    )
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    APP_URL: str = os.getenv("APP_URL", "http://web:8000")


settings = Settings()