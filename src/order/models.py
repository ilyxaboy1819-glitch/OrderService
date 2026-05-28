import uuid
from datetime import datetime
from enum import Enum

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class OrderStatus(str, Enum):
    NEW = "new"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(sa.UUID(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(sa.String(50), nullable=False, server_default=OrderStatus.NEW.value)
    is_deleted: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, server_default=sa.text("false"))
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True, onupdate=sa.func.now()
    )
    user_email: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    user_name: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)

    items: Mapped[list["OrderItemModel"]] = relationship(
        "OrderItemModel", back_populates="order", cascade="all, delete-orphan"
    )


class OrderItemModel(Base):
    __tablename__ = "order_items"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True), sa.ForeignKey("orders.id", ondelete="CASCADE")
    )
    application_id: Mapped[uuid.UUID] = mapped_column(sa.UUID(as_uuid=True), nullable=False)
    quantity: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    price: Mapped[float] = mapped_column(sa.Float, nullable=False)
    application_name: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)
    application_category: Mapped[str | None] = mapped_column(sa.String(255), nullable=True)

    order: Mapped["OrderModel"] = relationship("OrderModel", back_populates="items")
