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


class DocumentUploadResponse(BaseModel):
    document_id: int
    filename: str
    title: str
    file_type: str
    page_count: int | None
    chunk_count: int
    embedding_model: str
    vector_dimensions: int
    status: str


class DocumentSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    top_k: int = Field(default=3, ge=1, le=20)


class DocumentSearchResult(BaseModel):
    document_id: int
    chunk_id: int
    chunk_index: int
    page_number: int | None
    content: str
    score: float


class DocumentSearchResponse(BaseModel):
    query: str
    results: list[DocumentSearchResult]
