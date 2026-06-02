import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from src.order.models import OrderItemModel, OrderModel, OrderStatus


class OrderItemCreate(BaseModel):
    application_id: uuid.UUID
    quantity: int = Field(ge=1, le=100)
    price: float = Field(ge=0.0)
    application_name: str | None = None
    application_category: str | None = None


class OrderCreate(BaseModel):
    user_id: uuid.UUID
    user_email: str | None = None
    user_name: str | None = None
    idempotency_key: str | None = None
    items: list[OrderItemCreate] = Field(min_length=1, max_length=50)

    def to_model(self) -> OrderModel:
        return OrderModel(
            id=uuid.uuid4(),
            user_id=self.user_id,
            status=OrderStatus.NEW.value,
            user_email=self.user_email,
            user_name=self.user_name,
            idempotency_key=self.idempotency_key,
            items=[
                OrderItemModel(
                    id=uuid.uuid4(),
                    application_id=item.application_id,
                    quantity=item.quantity,
                    price=item.price,
                    application_name=item.application_name,
                    application_category=item.application_category,
                )
                for item in self.items
            ],
        )


class KafkaOrderPayload(BaseModel):
    user_id: str
    user_email: str | None = None
    user_name: str | None = None
    items: list[OrderItemCreate] = Field(min_length=1, max_length=50)
    idempotency_key: str


class OrderItemRead(BaseModel):
    application_id: uuid.UUID
    quantity: int
    price: float
    application_name: str | None = None
    application_category: str | None = None

    model_config = {"from_attributes": True}


class OrderRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    status: OrderStatus
    items: list[OrderItemRead]
    is_deleted: bool
    created_at: datetime
    updated_at: datetime | None = None
    user_email: str | None = None
    user_name: str | None = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, model: OrderModel) -> "OrderRead":
        return cls.model_validate(model)

    @classmethod
    def from_list(cls, models: List[OrderModel]) -> List["OrderRead"]:
        return [cls.from_model(m) for m in models]
