from typing import Any

from pydantic import BaseModel, Field


class CsAgentRequest(BaseModel):
    conversation_id: str | None = None
    message: str = Field(min_length=1, max_length=1000)


class ToolExecution(BaseModel):
    name: str
    arguments: dict[str, Any]
    result: dict[str, Any]


class CsAgentResponse(BaseModel):
    conversation_id: str
    answer: str
    tool_calls: list[ToolExecution]
    model: str


class PendingActionResponse(BaseModel):
    action_id: str
    conversation_id: str
    action_type: str
    order_id: int
    refund_amount: int
    status: str


class ActionApprovalResponse(PendingActionResponse):
    message: str
