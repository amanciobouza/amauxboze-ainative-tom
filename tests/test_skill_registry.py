from pathlib import Path

import pytest

from amauxboze.registries import AgentRegistry, AuthorizationService, SkillRegistry
from amauxboze.registries.schema_validation import SchemaValidationError


def test_loads_skills():
    registry = SkillRegistry(Path("skills"))
    skills = registry.load()
    assert "prepare-decision" in skills
    assert "summarize-status" in skills


def test_validates_skill_input():
    registry = SkillRegistry(Path("skills"))
    registry.load()

    registry.validate_input(
        "prepare-decision",
        {
            "question": "Launch now?",
            "options": ["launch", "wait"],
            "evidence": ["inventory ready"],
        },
    )


def test_rejects_invalid_skill_input():
    registry = SkillRegistry(Path("skills"))
    registry.load()

    with pytest.raises(SchemaValidationError):
        registry.validate_input("prepare-decision", {"question": "Launch now?"})


def test_agent_skill_authorization():
    agents = AgentRegistry(Path("runtime/agents"))
    skills = SkillRegistry(Path("skills"))
    agents.load()
    skills.load()

    auth = AuthorizationService(agents, skills)
    auth.authorize_skill("elena", "prepare-decision")

    with pytest.raises(PermissionError):
        auth.authorize_skill("maya", "prepare-decision")
