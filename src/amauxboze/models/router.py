from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

import httpx
from anthropic import Anthropic
from openai import OpenAI

Provider = Literal["lm_studio", "openai", "anthropic"]


@dataclass(frozen=True)
class RoutingRequest:
    privacy: str = "standard"
    reasoning: str = "medium"
    creativity: str = "medium"
    coding: bool = False
    preferred_providers: tuple[Provider, ...] = ()


class ModelRouter:
    def __init__(self, lm_studio_base_url: str = "http://127.0.0.1:1234"):
        self.lm_studio_base_url = lm_studio_base_url.rstrip("/")

    def lm_studio_available(self) -> bool:
        try:
            response = httpx.get(
                f"{self.lm_studio_base_url}/v1/models",
                timeout=2.0,
            )
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    def choose_provider(self, request: RoutingRequest) -> Provider:
        if request.privacy == "local_only":
            if not self.lm_studio_available():
                raise RuntimeError(
                    "Task is local-only but LM Studio is unavailable; cloud fallback is forbidden."
                )
            return "lm_studio"

        for provider in request.preferred_providers:
            if provider == "lm_studio" and not self.lm_studio_available():
                continue
            if provider == "openai" and not os.getenv("OPENAI_API_KEY"):
                continue
            if provider == "anthropic" and not os.getenv("ANTHROPIC_API_KEY"):
                continue
            return provider

        if self.lm_studio_available():
            return "lm_studio"
        if os.getenv("OPENAI_API_KEY"):
            return "openai"
        if os.getenv("ANTHROPIC_API_KEY"):
            return "anthropic"

        raise RuntimeError("No configured model provider is available.")

    def client(self, provider: Provider):
        if provider == "lm_studio":
            return OpenAI(base_url=f"{self.lm_studio_base_url}/v1", api_key="lm-studio")
        if provider == "openai":
            return OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        if provider == "anthropic":
            return Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        raise ValueError(f"Unsupported provider: {provider}")
