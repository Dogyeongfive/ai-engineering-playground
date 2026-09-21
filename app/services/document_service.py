from sqlalchemy.orm import Session

from app.repositories import document_repository
from app.services import chunking_service, embedding_service


def get_document(db: Session, document_id: int):
    return document_repository.get_document(db, document_id)


def list_documents(db: Session, offset: int, limit: int):
    return document_repository.list_documents(db, offset, limit)


def create_document(db: Session, title: str, content: str):
    return document_repository.create_document(db, title, content)


def embed_document(
    db: Session,
    document,
    chunk_size: int,
    overlap: int,
):
    chunks = chunking_service.chunk_text_recursive(
        document.content,
        chunk_size,
        overlap,
    )
    embeddings = embedding_service.create_embeddings(chunks)
    document_repository.replace_document_chunks(
        db,
        document.document_id,
        chunks,
        embeddings,
        embedding_service.EMBEDDING_MODEL,
    )

    return {
        "document_id": document.document_id,
        "chunk_count": len(chunks),
        "embedding_model": embedding_service.EMBEDDING_MODEL,
        "vector_dimensions": len(embeddings[0]) if embeddings else 0,
    }
