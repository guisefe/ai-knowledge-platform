"""create document version tables

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


document_version_status = postgresql.ENUM(
    "uploaded",
    "processing",
    "indexed",
    "failed",
    "deleted",
    name="document_version_status",
    create_type=False,
)


def upgrade() -> None:
    """Create logical documents and their immutable content versions."""
    document_version_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "documents",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("owner_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
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
    )
    op.create_index("ix_documents_owner_id", "documents", ["owner_id"], unique=False)

    op.create_table(
        "document_versions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=False),
        sa.Column("storage_key", sa.String(length=500), nullable=False),
        sa.Column(
            "status",
            document_version_status,
            server_default="uploaded",
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.false(),
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
        sa.CheckConstraint(
            "version_number > 0",
            name="ck_document_versions_positive_number",
        ),
        sa.CheckConstraint(
            "size_bytes >= 0",
            name="ck_document_versions_non_negative_size",
        ),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            name="fk_document_versions_document_id_documents",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_document_versions"),
        sa.UniqueConstraint(
            "document_id",
            "version_number",
            name="uq_document_versions_number",
        ),
        sa.UniqueConstraint(
            "document_id",
            "checksum_sha256",
            name="uq_document_versions_checksum",
        ),
        sa.UniqueConstraint(
            "storage_key",
            name="uq_document_versions_storage_key",
        ),
    )
    op.create_index(
        "ix_document_versions_document_id",
        "document_versions",
        ["document_id"],
        unique=False,
    )
    op.create_index(
        "ix_document_versions_status",
        "document_versions",
        ["status"],
        unique=False,
    )
    op.create_index(
        "uq_document_versions_one_active",
        "document_versions",
        ["document_id"],
        unique=True,
        postgresql_where=sa.text("is_active"),
    )


def downgrade() -> None:
    """Remove document versions and their logical documents."""
    op.drop_index("uq_document_versions_one_active", table_name="document_versions")
    op.drop_index("ix_document_versions_status", table_name="document_versions")
    op.drop_index("ix_document_versions_document_id", table_name="document_versions")
    op.drop_table("document_versions")
    op.drop_index("ix_documents_owner_id", table_name="documents")
    op.drop_table("documents")

    document_version_status.drop(op.get_bind(), checkfirst=True)
