import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends

from src.order.dependencies import get_order_service
from src.order.schemas import OrderCreate, OrderRead
from src.order.service import OrderService

router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])


@router.post("/", response_model=OrderRead, status_code=HTTPStatus.CREATED)
async def create_order(
    data: OrderCreate,
    service: OrderService = Depends(get_order_service),
) -> OrderRead:
    return await service.create(data)


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(
    order_id: uuid.UUID,
    service: OrderService = Depends(get_order_service),
) -> OrderRead:
    return await service.get_by_id(order_id)
