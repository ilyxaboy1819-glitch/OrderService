from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5434/orderservice"
    redis_url: str = "redis://localhost:6380"

    class Config:
        env_file = ".env"


settings = Settings()
