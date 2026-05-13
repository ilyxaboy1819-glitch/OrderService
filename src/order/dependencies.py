from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_session
from src.order.repository import OrderRepository
from src.order.service import OrderService

redis_client = Redis.from_url(settings.redis_url, decode_responses=True)


def get_order_service(
    session: AsyncSession = Depends(get_session),
) -> OrderService:
    return OrderService(
        repository=OrderRepository(session),
        redis=redis_client,
    )
