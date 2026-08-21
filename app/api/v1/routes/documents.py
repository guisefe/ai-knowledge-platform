from fastapi import APIRouter, HTTPException, Query, Response, status

from app.api.dependencies import CurrentUser, DatabaseSession
from app.domain.documents.schemas import (
    DocumentCreate,
    DocumentListResponse,
    DocumentResponse,
)
from app.domain.documents.service import DocumentNotFoundError, DocumentService

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
