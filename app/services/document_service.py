from sqlalchemy.orm import Session

from app.repositories import document_repository
from app.services import (
    chunking_service,
    embedding_service,
    vector_search_service,
)


def get_document(db: Session, document_id: int):
    return document_repository.get_document(db, document_id)


def list_documents(db: Session, offset: int, limit: int):
    return document_repository.list_documents(db, offset, limit)


def find_duplicate_document(
    db: Session,
    content_hash: str,
    content: str,
):
    return document_repository.find_duplicate_document(
        db,
        content_hash,
        content,
    )


def create_document(
    db: Session,
    title: str,
    content: str,
    content_hash: str | None = None,
):
    return document_repository.create_document(
        db,
        title,
        content,
        content_hash,
    )


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
    return embed_chunks(
        db,
        document.document_id,
        chunks,
        [None] * len(chunks),
    )


def embed_chunks(
    db: Session,
    document_id: int,
    chunks: list[str],
    page_numbers: list[int | None],
):
    embeddings = embedding_service.create_embeddings(chunks)
    document_repository.replace_document_chunks(
        db,
        document_id,
        chunks,
        embeddings,
        page_numbers,
        embedding_service.EMBEDDING_MODEL,
    )

    return {
        "document_id": document_id,
        "chunk_count": len(chunks),
        "embedding_model": embedding_service.EMBEDDING_MODEL,
        "vector_dimensions": len(embeddings[0]) if embeddings else 0,
    }


def search_document_chunks(db: Session, query: str, top_k: int):
    query_embedding = embedding_service.create_embeddings([query])[0]
    document_chunks = document_repository.list_document_chunks(db)
    scored_chunks = vector_search_service.find_similar_chunks(
        query_embedding,
        document_chunks,
        top_k,
    )

    return {
        "query": query,
        "results": [
            {
                "document_id": chunk.document_id,
                "chunk_id": chunk.chunk_id,
                "chunk_index": chunk.chunk_index,
                "page_number": chunk.page_number,
                "content": chunk.content,
                "score": score,
            }
            for chunk, score in scored_chunks
        ],
    }
