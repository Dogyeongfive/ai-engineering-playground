from datetime import datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cs import (
    CsConversation,
    CsMessage,
    CsPendingAction,
    Customer,
    Order,
)


def get_customer(db: Session, customer_id: int):
    return db.get(Customer, customer_id)


def get_order(db: Session, order_id: int):
    return db.get(Order, order_id)


def create_conversation(db: Session):
    conversation = CsConversation(conversation_id=str(uuid4()))
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def get_conversation(db: Session, conversation_id: str):
    return db.get(CsConversation, conversation_id)


def add_message(
    db: Session,
    conversation_id: str,
    role: str,
    content: str,
):
    message = CsMessage(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )
    conversation = get_conversation(db, conversation_id)
    if conversation is not None:
        conversation.updated_at = datetime.now()
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def list_recent_messages(
    db: Session,
    conversation_id: str,
    limit: int = 20,
):
    statement = (
        select(CsMessage)
        .where(CsMessage.conversation_id == conversation_id)
        .order_by(CsMessage.message_id.desc())
        .limit(limit)
    )
    messages = list(db.scalars(statement))
    messages.reverse()
    return messages


def get_pending_action(db: Session, action_id: str):
    return db.get(CsPendingAction, action_id)


def find_awaiting_cancellation(
    db: Session,
    conversation_id: str,
    order_id: int,
):
    statement = select(CsPendingAction).where(
        CsPendingAction.conversation_id == conversation_id,
        CsPendingAction.order_id == order_id,
        CsPendingAction.action_type == "cancel_order",
        CsPendingAction.status == "awaiting_approval",
    )
    return db.scalar(statement)


def create_cancellation_action(
    db: Session,
    conversation_id: str,
    order: Order,
):
    existing = find_awaiting_cancellation(
        db,
        conversation_id,
        order.order_id,
    )
    if existing is not None:
        return existing

    action = CsPendingAction(
        action_id=str(uuid4()),
        conversation_id=conversation_id,
        action_type="cancel_order",
        order_id=order.order_id,
        expected_order_status=order.status,
        refund_amount=order.amount,
        status="awaiting_approval",
    )
    db.add(action)
    db.commit()
    db.refresh(action)
    return action


def resolve_action(db: Session, action: CsPendingAction, status: str):
    action.status = status
    action.resolved_at = datetime.now()
    db.commit()
    db.refresh(action)
    return action
