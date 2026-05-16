import uuid

import pytest
from pydantic import ValidationError

from src.order.schemas import OrderCreate, OrderItemCreate


def test_valid_order_create():
    data = OrderCreate(
        user_id=uuid.uuid4(),
        items=[OrderItemCreate(application_id=uuid.uuid4(), quantity=2, price=9.99)],
    )
    assert len(data.items) == 1


def test_empty_items_rejected():
    with pytest.raises(ValidationError):
        OrderCreate(user_id=uuid.uuid4(), items=[])


def test_quantity_must_be_positive():
    with pytest.raises(ValidationError):
        OrderItemCreate(application_id=uuid.uuid4(), quantity=0, price=9.99)


def test_quantity_max_100():
    with pytest.raises(ValidationError):
        OrderItemCreate(application_id=uuid.uuid4(), quantity=101, price=9.99)


def test_price_cannot_be_negative():
    with pytest.raises(ValidationError):
        OrderItemCreate(application_id=uuid.uuid4(), quantity=1, price=-1.0)


def test_valid_order_item():
    item = OrderItemCreate(application_id=uuid.uuid4(), quantity=5, price=19.99)
    assert item.quantity == 5
    assert item.price == 19.99
