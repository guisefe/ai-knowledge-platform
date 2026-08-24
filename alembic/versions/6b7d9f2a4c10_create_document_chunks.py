"""create document chunks

Revision ID: 6b7d9f2a4c10
Revises: 20ec55748da8
Create Date: 2026-08-24
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6b7d9f2a4c10"
down_revision: str | Sequence[str] | None = "20ec55748da8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create ordered chunks with character-offset provenance."""
    op.create_table(
        "document_chunks",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("document_version_id", sa.String(length=36), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_sha256", sa.String(length=64), nullable=False),
        sa.Column("start_offset", sa.BigInteger(), nullable=False),
        sa.Column("end_offset", sa.BigInteger(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "position >= 0",
            name="ck_document_chunks_non_negative_position",
        ),
        sa.CheckConstraint(
            "start_offset >= 0",
            name="ck_document_chunks_non_negative_start",
        ),
        sa.CheckConstraint(
            "end_offset > start_offset",
            name="ck_document_chunks_ordered_offsets",
        ),
        sa.CheckConstraint(
            "char_length(content) > 0",
            name="ck_document_chunks_non_empty_content",
        ),
        sa.CheckConstraint(
            "char_length(content_sha256) = 64",
            name="ck_document_chunks_sha256_length",
        ),
        sa.ForeignKeyConstraint(
            ["document_version_id"],
            ["document_versions.id"],
            name="fk_document_chunks_document_version_id_document_versions",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_document_chunks"),
        sa.UniqueConstraint(
            "document_version_id",
            "position",
            name="uq_document_chunks_version_position",
        ),
    )


def downgrade() -> None:
    """Remove persisted document chunks."""
    op.drop_table("document_chunks")
