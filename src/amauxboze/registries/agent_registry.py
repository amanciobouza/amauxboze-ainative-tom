from __future__ import annotations

from pathlib import Path

import yaml

from .models import AgentManifest


class AgentRegistry:
    def __init__(self, manifest_dir: str | Path):
        self.manifest_dir = Path(manifest_dir)
        self._agents: dict[str, AgentManifest] = {}

    def load(self) -> dict[str, AgentManifest]:
        agents: dict[str, AgentManifest] = {}
        for path in sorted(self.manifest_dir.glob("*.yaml")):
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            manifest = AgentManifest.model_validate(raw)
            if manifest.id in agents:
                raise ValueError(f"Duplicate agent id: {manifest.id}")
            agents[manifest.id] = manifest
        self._agents = agents
        return agents

    def get(self, agent_id: str) -> AgentManifest:
        try:
            return self._agents[agent_id]
        except KeyError as exc:
            raise KeyError(f"Unknown agent: {agent_id}") from exc

    def assert_skill_allowed(self, agent_id: str, skill_id: str) -> None:
        agent = self.get(agent_id)
        if skill_id not in agent.skills:
            raise PermissionError(
                f"Agent '{agent_id}' is not allowed to use skill '{skill_id}'"
            )
