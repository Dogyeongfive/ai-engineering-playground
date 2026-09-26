from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.cs_agent import (
    ActionApprovalResponse,
    CsAgentRequest,
    CsAgentResponse,
)
from app.services import cs_agent_service

router = APIRouter(prefix="/cs-agent", tags=["cs-agent"])


@router.post("/chat", response_model=CsAgentResponse)
def chat(
    request: CsAgentRequest,
    db: Session = Depends(get_db),
):
    try:
        return cs_agent_service.chat(
            db,
            request.message,
            request.conversation_id,
        )
    except cs_agent_service.ConversationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        ) from error


@router.post(
    "/actions/{action_id}/approve",
    response_model=ActionApprovalResponse,
)
def approve_action(
    action_id: str,
    db: Session = Depends(get_db),
):
    action, error = cs_agent_service.approve_action(db, action_id)
    if error == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pending action not found",
        )
    if error is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error,
        )

    return {
        "action_id": action.action_id,
        "conversation_id": action.conversation_id,
        "action_type": action.action_type,
        "order_id": action.order_id,
        "refund_amount": action.refund_amount,
        "status": action.status,
        "message": "주문 취소가 승인되어 실행되었습니다.",
    }
