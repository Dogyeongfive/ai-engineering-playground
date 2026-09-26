import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy.orm import Session

from app.repositories import cs_repository
from app.services import cs_tool_service

load_dotenv()

AGENT_MODEL = os.getenv(
    "OPENAI_AGENT_MODEL",
    os.getenv("OPENAI_CHAT_MODEL", "gpt-5-mini"),
)
MAX_TOOL_ROUNDS = 5

AGENT_INSTRUCTIONS = """
당신은 온라인 쇼핑몰의 한국어 고객지원 에이전트입니다.
주문과 고객 정보는 추측하지 말고 반드시 제공된 도구로 조회하세요.
주문 취소 가능 여부를 묻는 경우 먼저 주문을 조회하고, 조회된 주문 상태로
취소 정책을 조회한 후 답하세요. 존재하지 않는 주문은 찾을 수 없다고 말하세요.
사용자가 취소 가능 여부만 질문하면 주문과 정책을 조회해 안내만 하세요.
사용자가 주문 취소를 명시적으로 요청하면 주문과 정책을 먼저 조회하고,
취소 가능할 때 propose_order_cancellation 도구로 승인 대기 요청을 만드세요.
승인 대기 요청은 주문을 실제로 취소하지 않습니다. 도구가 반환한 action_id와
승인 API를 사용자에게 안내하고, 승인 전에는 취소가 완료됐다고 말하지 마세요.
금액은 원 단위로 읽기 쉽게 표현하세요.
""".strip()


class ConversationNotFoundError(Exception):
    pass


def chat(
    db: Session,
    message: str,
    conversation_id: str | None = None,
):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    if conversation_id is None:
        conversation = cs_repository.create_conversation(db)
    else:
        conversation = cs_repository.get_conversation(db, conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(conversation_id)

    cs_repository.add_message(
        db,
        conversation.conversation_id,
        "user",
        message,
    )
    messages = cs_repository.list_recent_messages(
        db,
        conversation.conversation_id,
    )
    input_items = [
        {"role": item.role, "content": item.content}
        for item in messages
    ]
    execution_log = []

    for _ in range(MAX_TOOL_ROUNDS):
        response = client.responses.create(
            model=AGENT_MODEL,
            instructions=AGENT_INSTRUCTIONS,
            input=input_items,
            tools=cs_tool_service.TOOL_DEFINITIONS,
            parallel_tool_calls=False,
            store=False,
        )
        input_items += response.output
        function_calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]

        if not function_calls:
            answer = response.output_text
            cs_repository.add_message(
                db,
                conversation.conversation_id,
                "assistant",
                answer,
            )
            return {
                "conversation_id": conversation.conversation_id,
                "answer": answer,
                "tool_calls": execution_log,
                "model": AGENT_MODEL,
            }

        for function_call in function_calls:
            arguments = json.loads(function_call.arguments)
            result = cs_tool_service.execute_tool(
                db,
                function_call.name,
                arguments,
                conversation.conversation_id,
            )
            execution_log.append(
                {
                    "name": function_call.name,
                    "arguments": arguments,
                    "result": result,
                }
            )
            input_items.append(
                {
                    "type": "function_call_output",
                    "call_id": function_call.call_id,
                    "output": json.dumps(result, ensure_ascii=False),
                }
            )

    answer = (
        "도구 호출 횟수 제한에 도달했습니다. "
        "질문을 더 구체적으로 입력해주세요."
    )
    cs_repository.add_message(
        db,
        conversation.conversation_id,
        "assistant",
        answer,
    )
    return {
        "conversation_id": conversation.conversation_id,
        "answer": answer,
        "tool_calls": execution_log,
        "model": AGENT_MODEL,
    }


def approve_action(db: Session, action_id: str):
    action = cs_repository.get_pending_action(db, action_id)
    if action is None:
        return None, "not_found"
    if action.status != "awaiting_approval":
        return action, "already_resolved"

    order = cs_repository.get_order(db, action.order_id)
    if order is None:
        return action, "order_not_found"
    if order.status != action.expected_order_status:
        return action, "order_status_changed"

    policy = cs_tool_service.POLICIES.get(order.status)
    if policy is None or not policy["can_cancel"]:
        return action, "order_not_cancellable"

    order.status = "cancelled"
    cs_repository.resolve_action(db, action, "executed")
    return action, None
