from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class ProjectConfig(BaseModel):
    name: str
    repository: str


class KnowledgeConfig(BaseModel):
    provider: str = "obsidian"
    vault_path: str


class OrchestrationConfig(BaseModel):
    provider: str = "langgraph"


class LLMConfig(BaseModel):
    local_provider: str = "lm_studio"
    lm_studio_base_url: str = "http://127.0.0.1:1234"
    external_providers: list[str] = Field(default_factory=lambda: ["openai", "anthropic"])


class SoftwareDeliveryConfig(BaseModel):
    specification_standard: str = "OpenSpec"
    spec_driven: bool = True


class Settings(BaseModel):
    project: ProjectConfig
    knowledge: KnowledgeConfig
    orchestration: OrchestrationConfig
    llm: LLMConfig
    software_delivery: SoftwareDeliveryConfig

    @property
    def obsidian_vault(self) -> Path:
        override = os.getenv("OBSIDIAN_VAULT_PATH")
        return Path(override or self.knowledge.vault_path)

    @property
    def lm_studio_base_url(self) -> str:
        return os.getenv("LM_STUDIO_BASE_URL", self.llm.lm_studio_base_url)


def load_settings(path: str | Path = "config/project.yaml") -> Settings:
    config_path = Path(path)
    raw: dict[str, Any] = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    return Settings.model_validate(raw)
