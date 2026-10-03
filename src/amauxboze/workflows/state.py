from __future__ import annotations

from typing import Any, Literal, TypedDict


ApprovalStatus = Literal["not_required", "pending", "approved", "rejected", "revision_required"]


class WorkflowState(TypedDict, total=False):
    workflow_id: str
    workflow_name: str
    current_state: str
    agent_id: str
    skill_id: str
    model_provider: str
    approval_status: ApprovalStatus
    approval_reason: str
    payload: dict[str, Any]
    result: dict[str, Any]
    error: str
    side_effect_keys: list[str]
