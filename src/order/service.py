import logging
import uuid

from redis.asyncio import Redis

from src.order.exceptions import NotFoundException
from src.order.repository import OrderRepository
from src.order.schemas import OrderCreate, OrderRead

logger = logging.getLogger(__name__)

CACHE_TTL = 3600


class OrderService:

    def __init__(self, repository: OrderRepository, redis: Redis) -> None:
        self._repo = repository
        self._redis = redis

    async def create(self, data: OrderCreate) -> OrderRead:
        model = data.to_model()
        saved = await self._repo.create(model)
        logger.info(f"Order created with id={saved.id}")
        return OrderRead.from_model(saved)

    async def get_by_id(self, order_id: uuid.UUID) -> OrderRead:
        cache_key = f"order:{order_id}"

        cached = await self._redis.get(cache_key)
        if cached:
            logger.debug(f"Cache hit for order {order_id}")
            return OrderRead.model_validate_json(cached)

        model = await self._repo.get_by_id(order_id)
        if not model:
            raise NotFoundException(f"Order with id={order_id} not found")

        result = OrderRead.from_model(model)
        await self._redis.set(cache_key, result.model_dump_json(), ex=CACHE_TTL)
        return result
