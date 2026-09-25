from pydantic import BaseModel, Field


class RagChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    top_k: int = Field(default=3, ge=1, le=20)
    min_score: float = Field(default=0.3, ge=-1.0, le=1.0)


class RagSource(BaseModel):
    document_id: int
    chunk_id: int
    chunk_index: int
    page_number: int | None
    content: str
    score: float


class RagChatResponse(BaseModel):
    question: str
    answer: str
    sources: list[RagSource]
    model: str | None
