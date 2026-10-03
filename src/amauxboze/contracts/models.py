from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ContextRequest(BaseModel):
    task: str
    agent_id: str
    workflow_id: str | None = None
    knowledge_scopes: list[str] = Field(default_factory=list)
    max_items: int = 20
    max_chars: int = 20000


class ContextItem(BaseModel):
    source: str
    content: str
    provenance: dict[str, Any] = Field(default_factory=dict)


class ContextBundle(BaseModel):
    items: list[ContextItem] = Field(default_factory=list)
    role_context: dict[str, Any] = Field(default_factory=dict)
    workflow_context: dict[str, Any] = Field(default_factory=dict)


class ToolRequest(BaseModel):
    agent_id: str
    skill_id: str
    tool_name: str
    mode: Literal["read", "write", "action"]
    payload: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str | None = None


class ToolResult(BaseModel):
    status: Literal["ok", "error", "blocked"]
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class ModelRequest(BaseModel):
    task: str
    prompt: str
    privacy: str = "standard"
    reasoning: str = "medium"
    creativity: str = "medium"
    coding: bool = False
    preferred_providers: list[str] = Field(default_factory=list)


class ModelResponse(BaseModel):
    provider: str
    model: str | None = None
    content: str
    usage: dict[str, Any] = Field(default_factory=dict)
    latency_ms: int | None = None


class KnowledgeQuery(BaseModel):
    query: str
    scopes: list[str] = Field(default_factory=list)
    limit: int = 20


class KnowledgeDocument(BaseModel):
    path: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeWrite(BaseModel):
    path: str
    content: str
    workflow_id: str
    agent_id: str
    skill_id: str


class RuntimeEvent(BaseModel):
    event_id: str
    type: str
    timestamp: datetime
    source: str
    subject: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    correlation_id: str | None = None


class TraceSpan(BaseModel):
    trace_id: str
    span_id: str
    parent_span_id: str | None = None
    kind: str
    name: str
    started_at: datetime
    ended_at: datetime | None = None
    status: str = "running"
    attributes: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class PluginManifest(BaseModel):
    id: str
    version: str
    plugin_type: Literal[
        "model_provider",
        "tool_provider",
        "knowledge_provider",
        "event_source",
        "workflow_pack",
        "skill_pack",
    ]
    capabilities: list[str] = Field(default_factory=list)
    config_schema: dict[str, Any] = Field(default_factory=dict)
    health_check: bool = True
