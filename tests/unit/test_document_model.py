import pytest
from sqlalchemy import Index, UniqueConstraint

from app.domain.documents.models import (
    Document,
    DocumentVersion,
    DocumentVersionStatus,
    InvalidDocumentVersionTransition,
)


def make_version(
    status: DocumentVersionStatus = DocumentVersionStatus.UPLOADED,
) -> DocumentVersion:
    return DocumentVersion(
        document_id="document-id",
        version_number=1,
        original_filename="operations-policy.md",
        content_type="text/markdown",
        size_bytes=1024,
        checksum_sha256="a" * 64,
        storage_key="documents/owner-id/document-id/1.md",
        status=status,
        is_active=False,
    )


def test_document_soft_delete_is_idempotent() -> None:
    document = Document(owner_id="owner-id", title="Operations policy")

    document.soft_delete()
    first_deleted_at = document.deleted_at
    document.soft_delete()

    assert first_deleted_at is not None
    assert document.deleted_at == first_deleted_at


def test_uploaded_version_can_start_processing() -> None:
    version = make_version()

    version.start_processing()

    assert version.status is DocumentVersionStatus.PROCESSING
    assert version.error_message is None


def test_failed_version_can_be_retried() -> None:
    version = make_version(DocumentVersionStatus.FAILED)
    version.error_message = "embedding provider timed out"

    version.start_processing()

    assert version.status is DocumentVersionStatus.PROCESSING
    assert version.error_message is None


def test_version_cannot_skip_processing() -> None:
    version = make_version()

    with pytest.raises(InvalidDocumentVersionTransition):
        version.mark_indexed()


def test_processing_failure_requires_a_reason() -> None:
    version = make_version(DocumentVersionStatus.PROCESSING)

    with pytest.raises(ValueError, match="must include a reason"):
        version.mark_failed("   ")


def test_only_indexed_version_can_be_activated() -> None:
    version = make_version(DocumentVersionStatus.PROCESSING)

    with pytest.raises(InvalidDocumentVersionTransition, match="indexed"):
        version.activate()

    version.mark_indexed()
    version.activate()

    assert version.is_active is True


def test_deleting_a_version_removes_it_from_current_retrieval() -> None:
    version = make_version(DocumentVersionStatus.INDEXED)
    version.is_active = True

    version.mark_deleted()

    assert version.status is DocumentVersionStatus.DELETED
    assert version.is_active is False


def test_version_constraints_support_idempotency() -> None:
    constraints = {
        constraint.name: constraint
        for constraint in DocumentVersion.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }

    assert {column.name for column in constraints["uq_document_versions_number"].columns} == {
        "document_id",
        "version_number",
    }
    assert {column.name for column in constraints["uq_document_versions_checksum"].columns} == {
        "document_id",
        "checksum_sha256",
    }


def test_database_allows_only_one_active_version_per_document() -> None:
    active_index = next(
        index
        for index in DocumentVersion.__table__.indexes
        if isinstance(index, Index) and index.name == "uq_document_versions_one_active"
    )

    assert active_index.unique is True
    assert {column.name for column in active_index.columns} == {"document_id"}
