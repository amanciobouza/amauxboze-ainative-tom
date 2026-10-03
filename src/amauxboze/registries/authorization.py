from __future__ import annotations

from .agent_registry import AgentRegistry
from .skill_registry import SkillRegistry


class AuthorizationService:
    def __init__(self, agents: AgentRegistry, skills: SkillRegistry):
        self.agents = agents
        self.skills = skills

    def authorize_skill(self, agent_id: str, skill_id: str) -> None:
        self.agents.assert_skill_allowed(agent_id, skill_id)
        self.skills.get(skill_id)

    def authorize_tool(self, agent_id: str, tool_name: str, *, mode: str = "read") -> None:
        agent = self.agents.get(agent_id)

        if mode == "read":
            allowed = agent.tools.read
        elif mode == "write":
            allowed = agent.tools.write
        elif mode == "action":
            allowed = agent.tools.actions
        else:
            raise ValueError(f"Unsupported tool mode: {mode}")

        if tool_name not in allowed:
            raise PermissionError(
                f"Agent '{agent_id}' is not allowed to use tool '{tool_name}' in mode '{mode}'"
            )
