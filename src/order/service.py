import logging
import uuid
from typing import Optional

from redis.asyncio import Redis
from redis.exceptions import RedisError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.order.exceptions import NotFoundException
from src.order.repository import OrderRepository
from src.order.schemas import OrderCreate, OrderRead

logger = logging.getLogger(__name__)

CACHE_TTL = 3600


def _redis_retry():
    return retry(
        retry=retry_if_exception_type(RedisError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.1, min=0.1, max=0.5),
        reraise=True,
    )


class OrderService:

    def __init__(self, repository: OrderRepository, redis: Redis) -> None:
        self._repo = repository
        self._redis = redis

    async def create(self, data: OrderCreate) -> OrderRead:
        model = data.to_model()
        saved = await self._repo.create(model)
        result = OrderRead.from_model(saved)
        logger.info(f"Order created with id={saved.id}")
        return result

    async def get_by_id(self, order_id: uuid.UUID) -> OrderRead:
        cache_key = f"order:{order_id}"

        cached = await self._safe_cache_get(cache_key)
        if cached:
            logger.debug(f"Cache hit for order {order_id}")
            return OrderRead.model_validate_json(cached)

        model = await self._repo.get_by_id(order_id)
        if not model:
            raise NotFoundException(f"Order with id={order_id} not found")

        result = OrderRead.from_model(model)
        await self._safe_cache_set(cache_key, result.model_dump_json())
        return result

    async def _safe_cache_get(self, key: str) -> Optional[str]:
        try:
            return await self._retry_get(key)
        except RedisError as e:
            logger.warning(f"Redis get failed after retries: {e}")
            return None

    async def _safe_cache_set(self, key: str, value: str) -> None:
        try:
            await self._retry_set(key, value)
        except RedisError as e:
            logger.warning(f"Redis set failed after retries: {e}")

    @_redis_retry()
    async def _retry_get(self, key: str) -> Optional[str]:
        return await self._redis.get(key)

    @_redis_retry()
    async def _retry_set(self, key: str, value: str) -> None:
        await self._redis.set(key, value, ex=CACHE_TTL)
