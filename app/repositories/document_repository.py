import json

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentChunk


def get_document(db: Session, document_id: int):
    return db.get(Document, document_id)


def list_documents(db: Session, offset: int, limit: int):
    statement = (
        select(Document)
        .order_by(Document.document_id)
        .offset(offset)
        .limit(limit)
    )
    return db.scalars(statement).all()


def find_duplicate_document(
    db: Session,
    content_hash: str,
    content: str,
):
    statement = select(Document).where(
        (Document.content_hash == content_hash)
        | (
            (Document.content_hash.is_(None))
            & (Document.content == content)
        )
    )
    return db.scalars(statement).first()


def create_document(
    db: Session,
    title: str,
    content: str,
    content_hash: str | None = None,
):
    document = Document(
        title=title,
        content=content,
        content_hash=content_hash,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def replace_document_chunks(
    db: Session,
    document_id: int,
    chunks: list[str],
    embeddings: list[list[float]],
    page_numbers: list[int | None],
    embedding_model: str,
):
    db.execute(
        delete(DocumentChunk).where(
            DocumentChunk.document_id == document_id
        )
    )

    document_chunks = [
        DocumentChunk(
            document_id=document_id,
            chunk_index=index,
            page_number=page_number,
            content=content,
            embedding=json.dumps(embedding),
            embedding_model=embedding_model,
        )
        for index, (content, embedding, page_number) in enumerate(
            zip(chunks, embeddings, page_numbers, strict=True)
        )
    ]
    db.add_all(document_chunks)
    db.commit()
    return document_chunks


def list_document_chunks(db: Session):
    statement = select(DocumentChunk).order_by(DocumentChunk.chunk_id)
    return db.scalars(statement).all()
