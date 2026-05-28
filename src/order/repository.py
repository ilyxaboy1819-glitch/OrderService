import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.order.models import OrderModel


class OrderRepository:

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, model: OrderModel) -> OrderModel:
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model, ["items"])
        return model

    async def get_by_id(self, order_id: uuid.UUID) -> OrderModel | None:
        result = await self._session.execute(
            select(OrderModel)
            .where(OrderModel.id == order_id, OrderModel.is_deleted == False)
            .options(selectinload(OrderModel.items))
        )
        return result.scalar_one_or_none()
