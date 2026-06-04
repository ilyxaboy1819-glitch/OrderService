from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5434/orderservice"
    redis_url: str = "redis://localhost:6380"
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic: str = "orders"
    kafka_dlq_topic: str = "orders.dlq"
    kafka_group_id: str = "order-service"

    class Config:
        env_file = ".env"


settings = Settings()
