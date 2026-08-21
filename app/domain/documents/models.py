from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.database import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class DocumentVersionStatus(StrEnum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"
    DELETED = "deleted"


class InvalidDocumentVersionTransition(ValueError):
    pass


class Document(Base):
    """Logical document identity shared by all uploaded versions."""

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    owner_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    versions: Mapped[list[DocumentVersion]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def soft_delete(self) -> None:
        if self.deleted_at is None:
            self.deleted_at = utc_now()
            self.updated_at = self.deleted_at


class DocumentVersion(Base):
    """Immutable uploaded content and its processing lifecycle."""

    __tablename__ = "document_versions"
    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "version_number",
            name="uq_document_versions_number",
        ),
        UniqueConstraint(
            "document_id",
            "checksum_sha256",
            name="uq_document_versions_checksum",
        ),
        UniqueConstraint("storage_key", name="uq_document_versions_storage_key"),
        CheckConstraint("version_number > 0", name="ck_document_versions_positive_number"),
        CheckConstraint("size_bytes >= 0", name="ck_document_versions_non_negative_size"),
        Index(
            "uq_document_versions_one_active",
            "document_id",
            unique=True,
            postgresql_where=text("is_active"),
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[DocumentVersionStatus] = mapped_column(
        SqlEnum(
            DocumentVersionStatus,
            name="document_version_status",
            values_callable=lambda values: [item.value for item in values],
        ),
        default=DocumentVersionStatus.UPLOADED,
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    document: Mapped[Document] = relationship(back_populates="versions")

    def start_processing(self) -> None:
        self._transition_to(
            DocumentVersionStatus.PROCESSING,
            allowed_from={DocumentVersionStatus.UPLOADED, DocumentVersionStatus.FAILED},
        )
        self.error_message = None

    def mark_indexed(self) -> None:
        self._transition_to(
            DocumentVersionStatus.INDEXED,
            allowed_from={DocumentVersionStatus.PROCESSING},
        )
        self.error_message = None

    def mark_failed(self, reason: str) -> None:
        normalized_reason = reason.strip()
        if not normalized_reason:
            raise ValueError("A processing failure must include a reason")

        self._transition_to(
            DocumentVersionStatus.FAILED,
            allowed_from={DocumentVersionStatus.PROCESSING},
        )
        self.error_message = normalized_reason
        self.is_active = False

    def activate(self) -> None:
        if self.status is not DocumentVersionStatus.INDEXED:
            raise InvalidDocumentVersionTransition("Only an indexed version can be activated")
        self.is_active = True
        self.updated_at = utc_now()

    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = utc_now()

    def mark_deleted(self) -> None:
        if self.status is DocumentVersionStatus.DELETED:
            return
        self.status = DocumentVersionStatus.DELETED
        self.is_active = False
        self.updated_at = utc_now()

    def _transition_to(
        self,
        target: DocumentVersionStatus,
        *,
        allowed_from: set[DocumentVersionStatus],
    ) -> None:
        if self.status not in allowed_from:
            raise InvalidDocumentVersionTransition(
                f"Cannot transition document version from {self.status.value} to {target.value}"
            )
        self.status = target
        self.updated_at = utc_now()
