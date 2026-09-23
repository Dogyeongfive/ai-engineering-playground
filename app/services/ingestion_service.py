from pathlib import Path

from sqlalchemy.orm import Session

from app.services import document_service, parsing_service


def ingest_txt(
    db: Session,
    filename: str,
    file_bytes: bytes,
    chunk_size: int,
    overlap: int,
):
    content = parsing_service.parse_txt(filename, file_bytes)
    title = Path(filename).stem[:200]
    document = document_service.create_document(db, title, content)

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

    return {
        "document_id": document.document_id,
        "filename": filename,
        "title": document.title,
        "chunk_count": embedding_result["chunk_count"],
        "embedding_model": embedding_result["embedding_model"],
        "vector_dimensions": embedding_result["vector_dimensions"],
        "status": "ready",
    }
