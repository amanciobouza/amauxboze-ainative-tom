from __future__ import annotations

from amauxboze.contracts import PolicyEngine, ToolRequest
from amauxboze.registries import AuthorizationService


class RegistryPolicyEngine(PolicyEngine):
    def __init__(self, authorization: AuthorizationService):
        self.authorization = authorization

    def authorize_skill(self, agent_id: str, skill_id: str) -> None:
        self.authorization.authorize_skill(agent_id, skill_id)

    def authorize_tool(self, request: ToolRequest) -> None:
        self.authorization.authorize_tool(
            request.agent_id,
            request.tool_name,
            mode=request.mode,
        )

    def requires_approval(self, request: ToolRequest) -> bool:
        agent = self.authorization.agents.get(request.agent_id)
        return request.tool_name in agent.approval_boundaries
