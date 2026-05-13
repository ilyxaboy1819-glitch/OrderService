import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from src.order.models import OrderModel, OrderItemModel, OrderStatus
from src.order.schemas import OrderCreate, OrderItemCreate, OrderRead, OrderItemRead
from src.order.service import OrderService


def _make_order_model(**kwargs) -> OrderModel:
    model = OrderModel(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        status=OrderStatus.NEW.value,
        is_deleted=False,
        created_at=datetime.now(timezone.utc),
        items=[OrderItemModel(
            id=uuid.uuid4(),
            application_id=uuid.uuid4(),
            quantity=1,
            price=5.0,
        )],
    )
    for k, v in kwargs.items():
        setattr(model, k, v)
    return model


@pytest.fixture
def mock_repo():
    return AsyncMock()


@pytest.fixture
def mock_redis():
    redis = AsyncMock()
    redis.get.return_value = None
    return redis


@pytest.fixture
def service(mock_repo, mock_redis):
    return OrderService(repository=mock_repo, redis=mock_redis)


@pytest.mark.asyncio
async def test_create_order(service, mock_repo):
    model = _make_order_model()
    mock_repo.create.return_value = model

    data = OrderCreate(
        user_id=model.user_id,
        items=[OrderItemCreate(
            application_id=model.items[0].application_id,
            quantity=1,
            price=5.0,
        )],
    )
    result = await service.create(data)

    mock_repo.create.assert_called_once()
    assert result.user_id == model.user_id
    assert result.status == OrderStatus.NEW


@pytest.mark.asyncio
async def test_get_by_id_cache_miss(service, mock_repo, mock_redis):
    model = _make_order_model()
    mock_repo.get_by_id.return_value = model

    result = await service.get_by_id(model.id)

    mock_redis.get.assert_called_once()
    mock_repo.get_by_id.assert_called_once_with(model.id)
    mock_redis.set.assert_called_once()
    assert result is not None


@pytest.mark.asyncio
async def test_get_by_id_cache_hit(service, mock_repo, mock_redis):
    order_read = OrderRead(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        status=OrderStatus.NEW,
        items=[OrderItemRead(application_id=uuid.uuid4(), quantity=1, price=5.0)],
        is_deleted=False,
        created_at=datetime.now(timezone.utc),
    )
    mock_redis.get.return_value = order_read.model_dump_json()

    result = await service.get_by_id(order_read.id)

    mock_repo.get_by_id.assert_not_called()
    assert result.id == order_read.id


@pytest.mark.asyncio
async def test_get_by_id_not_found(service, mock_repo):
    mock_repo.get_by_id.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        await service.get_by_id(uuid.uuid4())
    assert exc_info.value.status_code == 404
