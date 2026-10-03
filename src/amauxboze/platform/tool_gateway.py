from __future__ import annotations

from collections.abc import Callable

from amauxboze.contracts import PolicyEngine, ToolGateway, ToolRequest, ToolResult, TraceRecorder

ToolHandler = Callable[[dict], dict]


class DefaultToolGateway(ToolGateway):
    def __init__(self, policy: PolicyEngine, trace: TraceRecorder | None = None):
        self.policy = policy
        self.trace = trace
        self._handlers: dict[str, ToolHandler] = {}
        self._idempotency: dict[str, ToolResult] = {}

    def register(self, tool_name: str, handler: ToolHandler) -> None:
        self._handlers[tool_name] = handler

    def execute(self, request: ToolRequest) -> ToolResult:
        self.policy.authorize_tool(request)

        if request.idempotency_key and request.idempotency_key in self._idempotency:
            return self._idempotency[request.idempotency_key]

        handler = self._handlers.get(request.tool_name)
        if handler is None:
            return ToolResult(status="error", error=f"Unknown tool: {request.tool_name}")

        try:
            data = handler(request.payload)
            result = ToolResult(status="ok", data=data)
        except Exception as exc:
            result = ToolResult(status="error", error=f"{type(exc).__name__}: {exc}")

        if request.idempotency_key and result.status == "ok":
            self._idempotency[request.idempotency_key] = result

        return result
