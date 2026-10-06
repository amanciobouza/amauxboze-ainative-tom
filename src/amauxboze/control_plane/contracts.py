from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class DTO(BaseModel):
    model_config = ConfigDict(extra="forbid")


Mode = Literal["live", "simulation"]
RunStatus = Literal["queued", "running", "waiting_approval", "held", "failed", "completed", "rejected", "cancelled"]


class Run(DTO):
    id: str
    process_id: str
    version: str = "1"
    title: str
    mode: Mode
    status: RunStatus = "queued"
    current_stage: str = "queued"
    active_agent_ids: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=now)
    updated_at: str = Field(default_factory=now)
    completed_at: str | None = None
    revision: int = 0
    input: dict[str, Any]
    state: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    approval_id: str | None = None
    allowed_commands: list[str] = Field(default_factory=list)
    pending_decision: dict[str, Any] | None = None


class Approval(DTO):
    id: str
    run_id: str
    revision: int
    action: str
    kind: Literal["approval", "recovery"] = "approval"
    allowed_decisions: list[str]
    context: dict[str, Any]
    status: Literal["pending", "resolved"] = "pending"
    decision: str | None = None
    rationale: str = ""
    created_at: str = Field(default_factory=now)

    checkpoint_id: str = ""


class StartCommand(DTO):
    process_id: str
    version: str = "1"
    mode: Mode = "live"
    input: dict[str, Any]
    idempotency_key: str = Field(min_length=8, max_length=128)


class DecisionCommand(DTO):
    decision: str
    revision: int = Field(ge=0)
    rationale: str = Field(default="", max_length=4000)
    idempotency_key: str = Field(min_length=8, max_length=128)


class RunCommand(DTO):
    revision: int = Field(ge=0)
    idempotency_key: str = Field(min_length=8, max_length=128)


class Event(DTO):
    id: int = 0
    run_id: str
    type: str
    timestamp: str = Field(default_factory=now)
    payload: dict[str, Any] = Field(default_factory=dict)


class StageAttempt(DTO):
    id: str
    run_id: str
    agent_id: str
    skill_id: str
    status: Literal["running", "completed", "failed"]
    attempt_number: int
    trace_id: str
    started_at: str = Field(default_factory=now)
    completed_at: str | None = None
    provider: str | None = None
    model: str | None = None
    usage: dict[str, Any] = Field(default_factory=dict)
    artifact: dict[str, Any] | None = None
    error: str | None = None


class Department(DTO):
    id: str
    name: str
    mission: str
    member_ids: list[str]


class OrganizationNode(DTO):
    id: str
    kind: Literal["human", "agent"]
    display_name: str
    role: str
    mission: str
    parent_id: str | None = None
    department_ids: list[str] = Field(default_factory=list)


class Organization(DTO):
    nodes: list[OrganizationNode]
    departments: list[Department]
    coordinator_id: str = "elena"


class ProcessDefinition(DTO):
    id: str
    version: str = "1"
    name: str
    description: str
    owner_department_id: str
    participant_department_ids: list[str]
    input_schema: dict[str, Any]
    approval_summary: str
    external_action: str | None = None
    live_limitation: str | None = None


class AppSettings(DTO):
    agent_language: Literal["de", "en"] = "de"
    vault_path: str
    lm_studio_url: str = "http://127.0.0.1:1234"
    provider: Literal["lm_studio", "openai", "anthropic"] = "lm_studio"
    model: str = ""
    privacy: Literal["local_only", "standard"] = "local_only"
    context_chars: int = Field(default=12000, ge=2000, le=24000)
    max_output_tokens: int = Field(default=4096, ge=256, le=16384)
    local_reasoning_effort: Literal["auto", "none", "low", "medium", "high"] = "auto"


class RetrospectiveStart(DTO):
    run_ids: list[str] = Field(min_length=1, max_length=5)
    title: str = Field(min_length=1, max_length=200)
    participant_ids: list[str] = Field(default_factory=lambda: ["elena", "nora"], min_length=1, max_length=4)
    idempotency_key: str = Field(min_length=8, max_length=128)


class Contribution(DTO):
    author_id: str
    evidence_refs: list[str]
    observation: str
    interpretation: str
    proposal: str
    evidence_gap: str


class Improvement(DTO):
    owner_id: str
    hypothesis: str
    baseline: str
    metric: str
    target: str
    risk: str
    openspec_ref: str | None = None


class Experiment(DTO):
    id: str
    improvement: Improvement
    status: Literal["proposed", "experimenting", "evaluating", "closed"] = "proposed"
    evidence: str = ""
    outcome: Literal["improved", "no_improvement", "inconclusive"] | None = None
    rationale: str = ""


class Retrospective(DTO):
    id: str
    title: str
    run_ids: list[str]
    participant_ids: list[str]
    mode: Mode
    status: Literal["draft", "collecting", "synthesizing", "awaiting_review", "approved", "rejected", "held", "experimenting", "evaluating", "closed", "failed"] = "draft"
    revision: int = 0
    created_at: str = Field(default_factory=now)
    updated_at: str = Field(default_factory=now)
    contributions: list[Contribution] = Field(default_factory=list)
    improvements: list[Improvement] = Field(default_factory=list)
    experiments: list[Experiment] = Field(default_factory=list)
    error: str | None = None
    exported_path: str | None = None


class ExperimentResult(DTO):
    revision: int
    outcome: Literal["improved", "no_improvement", "inconclusive"]
    evidence: str = Field(min_length=5, max_length=12000)
    rationale: str = Field(min_length=5, max_length=4000)
    idempotency_key: str = Field(min_length=8, max_length=128)
