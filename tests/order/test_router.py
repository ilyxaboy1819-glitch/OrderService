import uuid
from datetime import datetime, timezone
from http import HTTPStatus
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from src.order.dependencies import get_order_service
from src.order.exceptions import NotFoundException
from src.order.schemas import OrderRead, OrderItemRead
from src.order.models import OrderStatus


def _make_order_read() -> OrderRead:
    return OrderRead(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        status=OrderStatus.NEW,
        items=[OrderItemRead(application_id=uuid.uuid4(), quantity=1, price=5.0)],
        is_deleted=False,
        created_at=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_create_order(test_app, client: AsyncClient):
    order = _make_order_read()
    mock_service = AsyncMock()
    mock_service.create.return_value = order
    test_app.dependency_overrides[get_order_service] = lambda: mock_service

    response = await client.post(
        "/api/v1/orders/",
        json={
            "user_id": str(uuid.uuid4()),
            "items": [
                {
                    "application_id": str(uuid.uuid4()),
                    "quantity": 2,
                    "price": 9.99,
                }
            ],
        },
    )

    assert response.status_code == HTTPStatus.CREATED


@pytest.mark.asyncio
async def test_get_order_found(test_app, client: AsyncClient):
    order = _make_order_read()
    mock_service = AsyncMock()
    mock_service.get_by_id.return_value = order
    test_app.dependency_overrides[get_order_service] = lambda: mock_service

    response = await client.get(f"/api/v1/orders/{order.id}")

    assert response.status_code == HTTPStatus.OK
    assert response.json()["id"] == str(order.id)


@pytest.mark.asyncio
async def test_get_order_not_found(test_app, client: AsyncClient):
    mock_service = AsyncMock()
    mock_service.get_by_id.side_effect = NotFoundException("Order not found")
    test_app.dependency_overrides[get_order_service] = lambda: mock_service

    response = await client.get(f"/api/v1/orders/{uuid.uuid4()}")

    assert response.status_code == HTTPStatus.NOT_FOUND
