"""add idempotency_key to orders

Revision ID: 002
Revises: 001
Create Date: 2026-05-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    op.add_column('orders', sa.Column('idempotency_key', sa.String(36), nullable=False))
    op.create_unique_constraint('uq_orders_idempotency_key', 'orders', ['idempotency_key'])


def downgrade() -> None:
    op.drop_constraint('uq_orders_idempotency_key', 'orders', type_='unique')
    op.drop_column('orders', 'idempotency_key')
