"""add page number to document chunks

Revision ID: 4b9d2a6e71c0
Revises: b7e2c1d4a903
Create Date: 2026-09-23
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4b9d2a6e71c0"
down_revision: Union[str, Sequence[str], None] = "b7e2c1d4a903"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "document_chunks",
        sa.Column("page_number", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("document_chunks", "page_number")
