from typing import Annotated

from fastapi import APIRouter, File, HTTPException, Query, Response, UploadFile, status

from app.api.dependencies import CurrentUser, DatabaseSession, DocumentStorageDependency
from app.domain.documents.schemas import (
    DocumentCreate,
    DocumentListResponse,
    DocumentResponse,
    DocumentVersionUploadResponse,
)
from app.domain.documents.service import DocumentNotFoundError, DocumentService
from app.domain.documents.upload import (
    DocumentTooLargeError,
    DocumentUploadService,
    InvalidDocumentContentError,
    UnsupportedDocumentMediaTypeError,
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    payload: DocumentCreate,
    current_user: CurrentUser,
    session: DatabaseSession,
) -> DocumentResponse:
    document = await DocumentService(session).create(
        owner_id=current_user.id,
        title=payload.title,
    )
    await session.commit()
    return DocumentResponse.model_validate(document)


@router.post(
    "/{document_id}/versions",
    response_model=DocumentVersionUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document_version(
    document_id: str,
    response: Response,
    file: Annotated[UploadFile, File()],
    current_user: CurrentUser,
    session: DatabaseSession,
    storage: DocumentStorageDependency,
) -> DocumentVersionUploadResponse:
    try:
        result = await DocumentUploadService(session, storage).upload(
            file,
            owner_id=current_user.id,
            document_id=document_id,
            filename=file.filename,
            content_type=file.content_type,
        )
    except DocumentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        ) from exc
    except UnsupportedDocumentMediaTypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=str(exc),
        ) from exc
    except DocumentTooLargeError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=str(exc),
        ) from exc
    except InvalidDocumentContentError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    finally:
        await file.close()

    response.status_code = status.HTTP_201_CREATED if result.created else status.HTTP_200_OK
    version = result.version
    return DocumentVersionUploadResponse(
        id=version.id,
        document_id=version.document_id,
        version_number=version.version_number,
        original_filename=version.original_filename,
        content_type=version.content_type,
        size_bytes=version.size_bytes,
        checksum_sha256=version.checksum_sha256,
        status=version.status,
        created_at=version.created_at,
        created=result.created,
    )


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    current_user: CurrentUser,
    session: DatabaseSession,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> DocumentListResponse:
    page = await DocumentService(session).list(
        owner_id=current_user.id,
        limit=limit,
        offset=offset,
    )
    return DocumentListResponse(
        items=[DocumentResponse.model_validate(document) for document in page.items],
        total=page.total,
        limit=limit,
        offset=offset,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: CurrentUser,
    session: DatabaseSession,
) -> DocumentResponse:
    try:
        document = await DocumentService(session).get(
            owner_id=current_user.id,
            document_id=document_id,
        )
    except DocumentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        ) from exc

    return DocumentResponse.model_validate(document)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    current_user: CurrentUser,
    session: DatabaseSession,
) -> Response:
    try:
        await DocumentService(session).soft_delete(
            owner_id=current_user.id,
            document_id=document_id,
        )
        await session.commit()
    except DocumentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
