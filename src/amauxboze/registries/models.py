from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ToolPermissions(BaseModel):
    read: list[str] = Field(default_factory=list)
    write: list[str] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list)


class AgentManifest(BaseModel):
    id: str
    name: str
    role: str
    mission: str
    communication_instructions: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    tools: ToolPermissions = Field(default_factory=ToolPermissions)
    approval_boundaries: list[str] = Field(default_factory=list)


class ModelRequirements(BaseModel):
    privacy: str = "standard"
    reasoning: str = "medium"
    creativity: str = "medium"
    coding: bool = False
    preferred_providers: list[str] = Field(default_factory=list)


class SkillManifest(BaseModel):
    id: str
    version: str
    purpose: str
    inputs: dict[str, Any] = Field(default_factory=dict)
    outputs: dict[str, Any] = Field(default_factory=dict)
    context: list[str] = Field(default_factory=list)
    allowed_tools: list[str] = Field(default_factory=list)
    model: ModelRequirements = Field(default_factory=ModelRequirements)
    approval_required: bool = False
