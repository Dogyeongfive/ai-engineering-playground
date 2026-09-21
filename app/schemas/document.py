from pydantic import BaseModel, ConfigDict, Field


class DocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_id: int
    title: str
    content: str


class DocumentChunkPreview(BaseModel):
    document_id: int
    chunk_size: int
    overlap: int
    strategy: str
    chunks: list[str]


class DocumentEmbeddingResponse(BaseModel):
    document_id: int
    chunk_count: int
    embedding_model: str
    vector_dimensions: int
