"""create documents table

Revision ID: 20ec55748da8
Revises: 8e7382f938e2
Create Date: 2026-08-21 16:49:25.772857
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20ec55748da8"
down_revision: str | Sequence[str] | None = "8e7382f938e2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


document_status = postgresql.ENUM(
    "uploaded",
    "processing",
    "indexed",
    "failed",
    "deleted",
    name="document_status",
    create_type=False,
)


def upgrade() -> None:
    """Create the documents table and its supporting indexes."""
    document_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "documents",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("owner_id", sa.String(length=36), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=False),
        sa.Column("storage_key", sa.String(length=500), nullable=False),
        sa.Column(
            "status",
            document_status,
            server_default="uploaded",
            nullable=False,
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
            name="fk_documents_owner_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_documents"),
        sa.UniqueConstraint(
            "owner_id",
            "checksum_sha256",
            name="uq_documents_owner_checksum",
        ),
        sa.UniqueConstraint(
            "storage_key",
            name="uq_documents_storage_key",
        ),
    )

    op.create_index(
        "ix_documents_owner_id",
        "documents",
        ["owner_id"],
        unique=False,
    )
    op.create_index(
        "ix_documents_status",
        "documents",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    """Remove the documents table and its enum type."""
    op.drop_index("ix_documents_status", table_name="documents")
    op.drop_index("ix_documents_owner_id", table_name="documents")
    op.drop_table("documents")

    document_status.drop(op.get_bind(), checkfirst=True)
