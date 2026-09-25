from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.rag import RagChatRequest, RagChatResponse
from app.services import rag_service

router = APIRouter(prefix="/rag-chat", tags=["rag"])


@router.post("", response_model=RagChatResponse)
def rag_chat(
    request: RagChatRequest,
    db: Session = Depends(get_db),
):
    return rag_service.answer_question(
        db,
        request.question,
        request.top_k,
        request.min_score,
    )
