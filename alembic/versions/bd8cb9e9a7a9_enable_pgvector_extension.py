"""enable pgvector extension

Revision ID: enable_pgvector_extension
Revises:
Create Date: 2026-08-20
"""

from collections.abc import Sequence

from alembic import op

revision: str = "enable_pgvector_extension"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS vector")
