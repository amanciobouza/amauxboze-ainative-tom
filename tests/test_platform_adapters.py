from pathlib import Path

import pytest

from amauxboze.adapters import ObsidianAdapter
from amauxboze.contracts import KnowledgeQuery, KnowledgeWrite, ToolRequest
from amauxboze.platform import ObsidianKnowledgeProvider, RegistryPolicyEngine
from amauxboze.registries import AgentRegistry, AuthorizationService, SkillRegistry


def test_knowledge_search_rejects_escaped_scope(tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()
    (tmp_path / "private.md").write_text("private", encoding="utf-8")
    provider = ObsidianKnowledgeProvider(ObsidianAdapter(vault))
    with pytest.raises(PermissionError):
        provider.search(KnowledgeQuery(query="private", scopes=[".. ".strip()]))


def test_obsidian_knowledge_provider_read_write_search(tmp_path: Path):
    provider = ObsidianKnowledgeProvider(ObsidianAdapter(tmp_path))

    provider.write(
        KnowledgeWrite(
            path="Brand/test.md",
            content="Purpose matters.",
            workflow_id="wf-1",
            agent_id="elodie",
            skill_id="write-product-story",
        )
    )

    doc = provider.read("Brand/test.md")
    assert "Purpose matters." in doc.content

    results = provider.search(KnowledgeQuery(query="Purpose"))
    assert len(results) == 1
    assert results[0].path == "Brand/test.md"


def test_policy_engine_wraps_existing_permissions():
    agents = AgentRegistry(Path("runtime/agents"))
    skills = SkillRegistry(Path("skills"))
    agents.load()
    skills.load()

    policy = RegistryPolicyEngine(AuthorizationService(agents, skills))
    policy.authorize_skill("maya", "create-campaign-content")
    policy.authorize_tool(
        ToolRequest(
            agent_id="maya",
            skill_id="create-campaign-content",
            tool_name="social_publish",
            mode="action",
        )
    )
