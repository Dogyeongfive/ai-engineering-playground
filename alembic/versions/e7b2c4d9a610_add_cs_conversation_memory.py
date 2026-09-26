"""add cs conversation memory and pending actions

Revision ID: e7b2c4d9a610
Revises: d3f6a1b8c240
Create Date: 2026-09-26
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e7b2c4d9a610"
down_revision: Union[str, Sequence[str], None] = "d3f6a1b8c240"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cs_conversations",
        sa.Column("conversation_id", sa.String(length=36), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("conversation_id"),
    )
    op.create_table(
        "cs_messages",
        sa.Column("message_id", sa.Integer(), nullable=False),
        sa.Column("conversation_id", sa.String(length=36), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.String(length=4000), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["cs_conversations.conversation_id"],
        ),
        sa.PrimaryKeyConstraint("message_id"),
    )
    op.create_index(
        "ix_cs_messages_conversation_id",
        "cs_messages",
        ["conversation_id"],
        unique=False,
    )
    op.create_table(
        "cs_pending_actions",
        sa.Column("action_id", sa.String(length=36), nullable=False),
        sa.Column("conversation_id", sa.String(length=36), nullable=False),
        sa.Column("action_type", sa.String(length=50), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column(
            "expected_order_status",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column("refund_amount", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["cs_conversations.conversation_id"],
        ),
        sa.ForeignKeyConstraint(["order_id"], ["orders.order_id"]),
        sa.PrimaryKeyConstraint("action_id"),
    )
    op.create_index(
        "ix_cs_pending_actions_conversation_id",
        "cs_pending_actions",
        ["conversation_id"],
        unique=False,
    )
    op.create_index(
        "ix_cs_pending_actions_order_id",
        "cs_pending_actions",
        ["order_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_cs_pending_actions_order_id",
        table_name="cs_pending_actions",
    )
    op.drop_index(
        "ix_cs_pending_actions_conversation_id",
        table_name="cs_pending_actions",
    )
    op.drop_table("cs_pending_actions")
    op.drop_index(
        "ix_cs_messages_conversation_id",
        table_name="cs_messages",
    )
    op.drop_table("cs_messages")
    op.drop_table("cs_conversations")
