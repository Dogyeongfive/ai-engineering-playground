"""create document chunks table

Revision ID: b7e2c1d4a903
Revises: 8f360e9c7dd7
Create Date: 2026-09-22
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b7e2c1d4a903"
down_revision: Union[str, Sequence[str], None] = "8f360e9c7dd7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "document_chunks",
        sa.Column("chunk_id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", sa.Text(), nullable=False),
        sa.Column("embedding_model", sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.document_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("chunk_id"),
        sa.UniqueConstraint(
            "document_id",
            "chunk_index",
            name="uq_document_chunks_document_index",
        ),
    )
    op.create_index(
        op.f("ix_document_chunks_document_id"),
        "document_chunks",
        ["document_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_document_chunks_document_id"),
        table_name="document_chunks",
    )
    op.drop_table("document_chunks")
