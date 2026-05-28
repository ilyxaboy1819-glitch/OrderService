"""initial tables

Revision ID: 001
Revises:
Create Date: 2026-05-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.order.models import OrderStatus

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    op.create_table(
        'orders',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default=OrderStatus.NEW.value),
        sa.Column('user_email', sa.String(255), nullable=True),
        sa.Column('user_name', sa.String(255), nullable=True),
        sa.Column('is_deleted', sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        'order_items',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('order_id', sa.UUID(as_uuid=True), sa.ForeignKey('orders.id', ondelete='CASCADE')),
        sa.Column('application_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.Integer, nullable=False),
        sa.Column('price', sa.Float, nullable=False),
        sa.Column('application_name', sa.String(255), nullable=True),
        sa.Column('application_category', sa.String(255), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('order_items')
    op.drop_table('orders')
