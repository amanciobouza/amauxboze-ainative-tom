from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

from .models import (
    ContextBundle,
    ContextRequest,
    KnowledgeDocument,
    KnowledgeQuery,
    KnowledgeWrite,
    ModelRequest,
    ModelResponse,
    PluginManifest,
    RuntimeEvent,
    ToolRequest,
    ToolResult,
    TraceSpan,
)


class ContextEngine(ABC):
    @abstractmethod
    def build(self, request: ContextRequest) -> ContextBundle:
        raise NotImplementedError


class ToolGateway(ABC):
    @abstractmethod
    def execute(self, request: ToolRequest) -> ToolResult:
        raise NotImplementedError


class ModelGateway(ABC):
    @abstractmethod
    def invoke(self, request: ModelRequest) -> ModelResponse:
        raise NotImplementedError


class KnowledgeProvider(ABC):
    @abstractmethod
    def read(self, path: str) -> KnowledgeDocument:
        raise NotImplementedError

    @abstractmethod
    def search(self, query: KnowledgeQuery) -> list[KnowledgeDocument]:
        raise NotImplementedError

    @abstractmethod
    def write(self, request: KnowledgeWrite) -> KnowledgeDocument:
        raise NotImplementedError

    @abstractmethod
    def list(self, scope: str = "") -> list[KnowledgeDocument]:
        raise NotImplementedError


class PolicyEngine(ABC):
    @abstractmethod
    def authorize_skill(self, agent_id: str, skill_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def authorize_tool(self, request: ToolRequest) -> None:
        raise NotImplementedError

    @abstractmethod
    def requires_approval(self, request: ToolRequest) -> bool:
        raise NotImplementedError


class EventEngine(ABC):
    @abstractmethod
    def publish(self, event: RuntimeEvent) -> None:
        raise NotImplementedError

    @abstractmethod
    def subscribe(self, event_type: str, handler) -> None:
        raise NotImplementedError


class TraceRecorder(ABC):
    @abstractmethod
    def record(self, span: TraceSpan) -> None:
        raise NotImplementedError


class PluginRegistry(ABC):
    @abstractmethod
    def register(self, manifest: PluginManifest, provider: object) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, plugin_id: str) -> object:
        raise NotImplementedError

    @abstractmethod
    def manifests(self) -> Iterable[PluginManifest]:
        raise NotImplementedError
