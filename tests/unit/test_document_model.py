from sqlalchemy import UniqueConstraint

from app.domain.documents.models import Document, DocumentStatus


def test_document_status_values_are_stable() -> None:
    assert [status.value for status in DocumentStatus] == [
        "uploaded",
        "processing",
        "indexed",
        "failed",
        "deleted",
    ]


def test_document_uses_expected_table() -> None:
    assert Document.__tablename__ == "documents"


def test_document_has_expected_columns() -> None:
    assert set(Document.__table__.columns.keys()) == {
        "id",
        "owner_id",
        "original_filename",
        "content_type",
        "size_bytes",
        "checksum_sha256",
        "storage_key",
        "status",
        "error_message",
        "created_at",
        "updated_at",
        "deleted_at",
    }


def test_document_prevents_duplicate_content_per_owner() -> None:
    constraints = [
        constraint
        for constraint in Document.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]

    owner_checksum_constraint = next(
        constraint for constraint in constraints if constraint.name == "uq_documents_owner_checksum"
    )

    assert {column.name for column in owner_checksum_constraint.columns} == {
        "owner_id",
        "checksum_sha256",
    }


def test_document_can_represent_an_uploaded_file() -> None:
    document = Document(
        owner_id="user-id",
        original_filename="the-grand-inquisitor.txt",
        content_type="text/plain",
        size_bytes=1024,
        checksum_sha256="a" * 64,
        storage_key="documents/user-id/document-id.txt",
        status=DocumentStatus.UPLOADED,
    )

    assert document.original_filename == "the-grand-inquisitor.txt"
    assert document.status is DocumentStatus.UPLOADED
    assert document.error_message is None
    assert document.deleted_at is None
