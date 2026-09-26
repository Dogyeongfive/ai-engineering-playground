from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.repositories import cs_repository


class GetOrderArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_id: int = Field(gt=0)


class GetCustomerArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: int = Field(gt=0)


class GetCancellationPolicyArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_status: Literal[
        "preparing",
        "shipped",
        "delivered",
        "cancelled",
    ]


class ProposeOrderCancellationArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_id: int = Field(gt=0)


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "name": "get_order",
        "description": (
            "주문 번호로 상품, 결제 금액, 주문 상태, 배송 정보를 조회합니다."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "integer",
                    "description": "조회할 주문 번호",
                }
            },
            "required": ["order_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_customer",
        "description": "고객 번호로 고객 이름과 이메일을 조회합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "integer",
                    "description": "조회할 고객 번호",
                }
            },
            "required": ["customer_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_cancellation_policy",
        "description": (
            "주문 상태에 맞는 취소·환불 정책과 처리 가능 여부를 조회합니다."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "order_status": {
                    "type": "string",
                    "enum": [
                        "preparing",
                        "shipped",
                        "delivered",
                        "cancelled",
                    ],
                    "description": "get_order가 반환한 주문 상태",
                }
            },
            "required": ["order_status"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "propose_order_cancellation",
        "description": (
            "고객이 주문 취소를 명시적으로 요청했을 때 승인 대기 요청을 "
            "생성합니다. 주문을 즉시 취소하지는 않습니다."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "integer",
                    "description": "취소 승인을 요청할 주문 번호",
                }
            },
            "required": ["order_id"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


POLICIES = {
    "preparing": {
        "can_cancel": True,
        "refund_rate": 1.0,
        "guidance": "출고 전 주문은 전액 환불로 취소할 수 있습니다.",
    },
    "shipped": {
        "can_cancel": False,
        "refund_rate": None,
        "guidance": (
            "이미 출고되어 즉시 취소할 수 없습니다. "
            "상품 수령 후 반품 절차를 안내해야 합니다."
        ),
    },
    "delivered": {
        "can_cancel": False,
        "refund_rate": None,
        "guidance": (
            "배송 완료 주문은 취소가 아닌 반품 대상입니다. "
            "반품 가능 기간과 상품 상태를 추가로 확인해야 합니다."
        ),
    },
    "cancelled": {
        "can_cancel": False,
        "refund_rate": 1.0,
        "guidance": "이미 취소된 주문입니다.",
    },
}


def execute_tool(
    db: Session,
    tool_name: str,
    arguments: dict,
    conversation_id: str | None = None,
):
    if tool_name == "get_order":
        args = GetOrderArgs.model_validate(arguments)
        order = cs_repository.get_order(db, args.order_id)
        if order is None:
            return {"found": False, "order_id": args.order_id}
        return {
            "found": True,
            "order_id": order.order_id,
            "customer_id": order.customer_id,
            "product_name": order.product_name,
            "amount": order.amount,
            "status": order.status,
            "tracking_number": order.tracking_number,
        }

    if tool_name == "get_customer":
        args = GetCustomerArgs.model_validate(arguments)
        customer = cs_repository.get_customer(db, args.customer_id)
        if customer is None:
            return {"found": False, "customer_id": args.customer_id}
        return {
            "found": True,
            "customer_id": customer.customer_id,
            "name": customer.name,
            "email": customer.email,
        }

    if tool_name == "get_cancellation_policy":
        args = GetCancellationPolicyArgs.model_validate(arguments)
        return {
            "order_status": args.order_status,
            **POLICIES[args.order_status],
        }

    if tool_name == "propose_order_cancellation":
        args = ProposeOrderCancellationArgs.model_validate(arguments)
        if conversation_id is None:
            return {"created": False, "reason": "conversation_required"}

        order = cs_repository.get_order(db, args.order_id)
        if order is None:
            return {
                "created": False,
                "reason": "order_not_found",
                "order_id": args.order_id,
            }

        policy = POLICIES.get(order.status)
        if policy is None or not policy["can_cancel"]:
            return {
                "created": False,
                "reason": "order_not_cancellable",
                "order_id": order.order_id,
                "order_status": order.status,
            }

        action = cs_repository.create_cancellation_action(
            db,
            conversation_id,
            order,
        )
        return {
            "created": True,
            "action_id": action.action_id,
            "action_type": action.action_type,
            "order_id": action.order_id,
            "refund_amount": action.refund_amount,
            "status": action.status,
            "next_step": (
                f"POST /cs-agent/actions/{action.action_id}/approve"
            ),
        }

    return {
        "error": "unknown_tool",
        "tool_name": tool_name,
    }
