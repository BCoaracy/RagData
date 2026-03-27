"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration — reads from env vars or .env file."""

    divine_pride_api_key: str = ""
    divine_pride_base_url: str = "https://divine-pride.net/api/database"
    database_url: str = "sqlite+aiosqlite:///./data/ro_optimizer.db"
    cache_ttl_hours: int = 24

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
