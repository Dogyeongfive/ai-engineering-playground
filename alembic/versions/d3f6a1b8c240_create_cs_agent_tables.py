"""create cs agent tables

Revision ID: d3f6a1b8c240
Revises: c8a4f7e2d910
Create Date: 2026-09-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d3f6a1b8c240"
down_revision: Union[str, Sequence[str], None] = "c8a4f7e2d910"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    customers = op.create_table(
        "customers",
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=200), nullable=False),
        sa.PrimaryKeyConstraint("customer_id"),
    )
    orders = op.create_table(
        "orders",
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("product_name", sa.String(length=200), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("tracking_number", sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.customer_id"]),
        sa.PrimaryKeyConstraint("order_id"),
    )
    op.create_index(
        "ix_orders_customer_id",
        "orders",
        ["customer_id"],
        unique=False,
    )

    op.bulk_insert(
        customers,
        [
            {
                "customer_id": 1,
                "name": "도경",
                "email": "dokyeong@example.com",
            },
            {
                "customer_id": 2,
                "name": "철수",
                "email": "cheolsu@example.com",
            },
        ],
    )
    op.bulk_insert(
        orders,
        [
            {
                "order_id": 1001,
                "customer_id": 1,
                "product_name": "무선 키보드",
                "amount": 59000,
                "status": "preparing",
                "tracking_number": None,
            },
            {
                "order_id": 1002,
                "customer_id": 1,
                "product_name": "노이즈 캔슬링 이어폰",
                "amount": 129000,
                "status": "shipped",
                "tracking_number": "KR-2026-1002",
            },
            {
                "order_id": 1003,
                "customer_id": 2,
                "product_name": "스테인리스 텀블러",
                "amount": 25000,
                "status": "delivered",
                "tracking_number": "KR-2026-1003",
            },
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_orders_customer_id", table_name="orders")
    op.drop_table("orders")
    op.drop_table("customers")
