from typing import Literal

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.document import (
    DocumentChunkPreview,
    DocumentCreate,
    DocumentEmbeddingResponse,
    DocumentResponse,
    DocumentSearchRequest,
    DocumentSearchResponse,
    DocumentUploadResponse,
)
from app.services import chunking_service, document_service, ingestion_service

router = APIRouter(prefix="/documents", tags=["documents"])
MAX_UPLOAD_BYTES = 10_000_000


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return document_service.list_documents(db, offset, limit)


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_document(
    request: DocumentCreate,
    db: Session = Depends(get_db),
):
    return document_service.create_document(
        db,
        request.title,
        request.content,
    )


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_document(
    file: UploadFile = File(...),
    chunk_size: int = Query(default=300, ge=50, le=2000),
    overlap: int = Query(default=50, ge=0, le=500),
    db: Session = Depends(get_db),
):
    if overlap >= chunk_size:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="overlap must be smaller than chunk_size",
        )

    filename = file.filename or ""
    file_bytes = file.file.read(MAX_UPLOAD_BYTES + 1)
    file.file.close()

    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="file must be 10 MB or smaller",
        )

    try:
        return ingestion_service.ingest_document(
            db,
            filename,
            file_bytes,
            chunk_size,
            overlap,
        )
    except ingestion_service.DuplicateDocumentError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Document already exists with document_id="
                f"{error.document_id}"
            ),
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error


@router.post("/search", response_model=DocumentSearchResponse)
def search_documents(
    request: DocumentSearchRequest,
    db: Session = Depends(get_db),
):
    return document_service.search_document_chunks(
        db,
        request.query,
        request.top_k,
    )


@router.post(
    "/{document_id}/chunk-preview",
    response_model=DocumentChunkPreview,
)
def preview_document_chunks(
    document_id: int,
    chunk_size: int = Query(default=300, ge=50, le=2000),
    overlap: int = Query(default=50, ge=0, le=500),
    strategy: Literal["fixed", "recursive"] = Query(default="recursive"),
    db: Session = Depends(get_db),
):
    if overlap >= chunk_size:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="overlap must be smaller than chunk_size",
        )

    document = document_service.get_document(db, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    if strategy == "fixed":
        chunks = chunking_service.chunk_text(
            document.content,
            chunk_size,
            overlap,
        )
    else:
        chunks = chunking_service.chunk_text_recursive(
            document.content,
            chunk_size,
            overlap,
        )

    return {
        "document_id": document_id,
        "chunk_size": chunk_size,
        "overlap": overlap,
        "strategy": strategy,
        "chunks": chunks,
    }


@router.post(
    "/{document_id}/embed",
    response_model=DocumentEmbeddingResponse,
    status_code=status.HTTP_201_CREATED,
)
def embed_document(
    document_id: int,
    chunk_size: int = Query(default=300, ge=50, le=2000),
    overlap: int = Query(default=50, ge=0, le=500),
    db: Session = Depends(get_db),
):
    if overlap >= chunk_size:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="overlap must be smaller than chunk_size",
        )

    document = document_service.get_document(db, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document_service.embed_document(
        db,
        document,
        chunk_size,
        overlap,
    )
