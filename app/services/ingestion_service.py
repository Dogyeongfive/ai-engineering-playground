import hashlib
from pathlib import Path

from sqlalchemy.orm import Session

from app.services import (
    chunking_service,
    document_service,
    parsing_service,
)


class DuplicateDocumentError(Exception):
    def __init__(self, document_id: int):
        self.document_id = document_id
        super().__init__(f"document already exists: {document_id}")


def ingest_document(
    db: Session,
    filename: str,
    file_bytes: bytes,
    chunk_size: int,
    overlap: int,
):
    extension = Path(filename).suffix.lower()

    if extension == ".txt":
        return _ingest_txt(
            db, filename, file_bytes, chunk_size, overlap
        )
    if extension == ".pdf":
        return _ingest_pdf(
            db, filename, file_bytes, chunk_size, overlap
        )

    raise ValueError("only .txt and .pdf files are supported")


def _ingest_txt(
    db: Session,
    filename: str,
    file_bytes: bytes,
    chunk_size: int,
    overlap: int,
):
    content = parsing_service.parse_txt(filename, file_bytes)
    title = Path(filename).stem[:200]
    document = _create_unique_document(db, title, content)

    try:
        embedding_result = document_service.embed_document(
            db,
            document,
            chunk_size,
            overlap,
        )
    except Exception:
        db.delete(document)
        db.commit()
        raise

    return _build_result(
        document,
        filename,
        "txt",
        None,
        embedding_result,
    )


def _ingest_pdf(
    db: Session,
    filename: str,
    file_bytes: bytes,
    chunk_size: int,
    overlap: int,
):
    parsed_pdf = parsing_service.parse_pdf(filename, file_bytes)
    content = "\n\n".join(page.text for page in parsed_pdf.pages)
    document = _create_unique_document(
        db,
        Path(filename).stem[:200],
        content,
    )

    chunks = []
    page_numbers = []
    for page in parsed_pdf.pages:
        page_chunks = chunking_service.chunk_text_recursive(
            page.text,
            chunk_size,
            overlap,
        )
        chunks.extend(page_chunks)
        page_numbers.extend([page.page_number] * len(page_chunks))

    try:
        embedding_result = document_service.embed_chunks(
            db,
            document.document_id,
            chunks,
            page_numbers,
        )
    except Exception:
        db.delete(document)
        db.commit()
        raise

    return _build_result(
        document,
        filename,
        "pdf",
        parsed_pdf.total_pages,
        embedding_result,
    )


def _create_unique_document(
    db: Session,
    title: str,
    content: str,
):
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    existing_document = document_service.find_duplicate_document(
        db,
        content_hash,
        content,
    )
    if existing_document is not None:
        raise DuplicateDocumentError(existing_document.document_id)

    return document_service.create_document(
        db,
        title,
        content,
        content_hash,
    )


def _build_result(
    document,
    filename: str,
    file_type: str,
    page_count: int | None,
    embedding_result: dict,
):
    return {
        "document_id": document.document_id,
        "filename": filename,
        "title": document.title,
        "file_type": file_type,
        "page_count": page_count,
        "chunk_count": embedding_result["chunk_count"],
        "embedding_model": embedding_result["embedding_model"],
        "vector_dimensions": embedding_result["vector_dimensions"],
        "status": "ready",
    }
