from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.domain.documents.models import DocumentVersionStatus

DocumentTitle = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=255),
]


class DocumentCreate(BaseModel):
    title: DocumentTitle


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)


class DocumentVersionUploadResponse(BaseModel):
    id: str
    document_id: str
    version_number: int = Field(ge=1)
    original_filename: str
    content_type: str
    size_bytes: int = Field(gt=0)
    checksum_sha256: str
    status: DocumentVersionStatus
    created_at: datetime
    created: bool
