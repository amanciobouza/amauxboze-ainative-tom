from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from langgraph.types import interrupt

ApprovalDecision = Literal["approve", "reject", "revise"]


@dataclass(frozen=True)
class ApprovalRequest:
    workflow_id: str
    action: str
    reason: str
    summary: str


def request_approval(request: ApprovalRequest) -> ApprovalDecision:
    response = interrupt(
        {
            "type": "approval_request",
            "workflow_id": request.workflow_id,
            "action": request.action,
            "reason": request.reason,
            "summary": request.summary,
            "allowed_decisions": ["approve", "reject", "revise"],
        }
    )

    decision = str(response).strip().lower()
    if decision not in {"approve", "reject", "revise"}:
        raise ValueError(f"Invalid approval decision: {decision}")
    return decision  # type: ignore[return-value]
