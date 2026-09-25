"""add content hash to documents

Revision ID: c8a4f7e2d910
Revises: 4b9d2a6e71c0
Create Date: 2026-09-23
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c8a4f7e2d910"
down_revision: Union[str, Sequence[str], None] = "4b9d2a6e71c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("content_hash", sa.String(length=64), nullable=True),
    )
    op.create_index(
        "ix_documents_content_hash",
        "documents",
        ["content_hash"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_documents_content_hash", table_name="documents")
    op.drop_column("documents", "content_hash")
