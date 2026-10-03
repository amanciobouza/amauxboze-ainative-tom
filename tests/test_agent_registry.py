from pathlib import Path

import pytest

from amauxboze.registries import AgentRegistry


def test_loads_agent_manifests():
    registry = AgentRegistry(Path("runtime/agents"))
    agents = registry.load()
    assert "elena" in agents
    assert "kai" in agents
    assert agents["lucien"].role == "Head of Product & Watch Design"


def test_rejects_unauthorized_skill():
    registry = AgentRegistry(Path("runtime/agents"))
    registry.load()
    with pytest.raises(PermissionError):
        registry.assert_skill_allowed("maya", "approve-production")
