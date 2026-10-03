from pathlib import Path

from langgraph.types import Command

from amauxboze.adapters import ObsidianAdapter
from amauxboze.registries import AgentRegistry, AuthorizationService, SkillRegistry
from amauxboze.workflows.content_campaign import (
    ContentCampaignDependencies,
    build_content_campaign_workflow,
)
from amauxboze.workflows.content_campaign_persistence import ContentCampaignPersistence


def stage_executor(agent, skill, payload):
    outputs = {
        "define-campaign-brief": {
            "objective": "Build awareness for Amaux Bozé",
            "audience": "Fathers 35-55",
            "constraints": [],
            "success_signals": ["engagement"],
        },
        "create-message-architecture": {
            "core_message": "Intent beats money.",
            "supporting_messages": ["Every watch says something."],
            "narrative_frame": "Know why you wear it.",
        },
        "assess-audience-relevance": {
            "relevance": "high",
            "objections": [],
            "misunderstandings": [],
        },
        "validate-campaign-evidence": {
            "supported_claims": ["The watch uses a mechanical movement."],
            "unsupported_claims": [],
            "evidence_notes": [],
        },
        "define-channel-strategy": {
            "channels": ["instagram", "tiktok"],
            "formats": ["short video", "carousel"],
            "cadence": ["day 1", "day 3"],
            "repurposing": ["video to carousel"],
        },
        "align-commercial-objective": {
            "cta": "Learn more",
            "destination": "shopify",
            "tracking": ["utm_campaign"],
            "conversion_notes": [],
        },
        "create-campaign-content": {
            "assets": ["video-1"],
            "copy": ["Intent beats money."],
            "schedule": ["day 1"],
        },
        "review-campaign-brand-fit": {
            "fit": "strong",
            "issues": [],
            "required_changes": [],
        },
        "capture-campaign-learning": {
            "what_worked": ["Clear message"],
            "what_did_not": [],
            "next_experiment": "Test stronger founder story",
        },
    }
    return outputs[skill]


def initial_state():
    return {
        "workflow_id": "campaign-1",
        "campaign_objective": "Build awareness",
        "audience": "Fathers 35-55",
    }


def build(publish_calls, *, persistence=None, execute_stage=stage_executor):
    agents = AgentRegistry(Path("runtime/agents"))
    skills = SkillRegistry(Path("skills"))
    agents.load()
    skills.load()

    def publish(payload):
        publish_calls.append(payload)
        return {"status": "published"}

    deps = ContentCampaignDependencies(
        skills=skills,
        authorization=AuthorizationService(agents, skills),
        execute_stage=execute_stage,
        execute_publish=publish,
        persistence=persistence,
    )
    return build_content_campaign_workflow(deps), agents


def test_happy_path_publishes_once_and_completes():
    calls = []
    graph, _ = build(calls)
    config = {"configurable": {"thread_id": "campaign-happy"}}

    first = graph.invoke(initial_state(), config=config)
    assert "__interrupt__" in first

    final = graph.invoke(Command(resume="approve"), config=config)
    assert final["current_state"] == "COMPLETE"
    assert final["published"] is True
    assert len(calls) == 1


def test_revision_returns_to_content_and_gates_again():
    calls = []
    graph, _ = build(calls)
    config = {"configurable": {"thread_id": "campaign-revise"}}

    graph.invoke(initial_state(), config=config)
    second = graph.invoke(Command(resume="revise"), config=config)

    assert "__interrupt__" in second
    assert calls == []


def test_hold_path():
    calls = []
    graph, _ = build(calls)
    config = {"configurable": {"thread_id": "campaign-hold"}}

    graph.invoke(initial_state(), config=config)
    final = graph.invoke(Command(resume="hold"), config=config)

    assert final["current_state"] == "ON_HOLD"
    assert calls == []


def test_cancel_path():
    calls = []
    graph, _ = build(calls)
    config = {"configurable": {"thread_id": "campaign-cancel"}}

    graph.invoke(initial_state(), config=config)
    final = graph.invoke(Command(resume="cancel"), config=config)

    assert final["current_state"] == "CANCELLED"
    assert calls == []


def test_unauthorized_publish_enters_error_state():
    calls = []
    graph, agents = build(calls)
    agents._agents["maya"].tools.actions = []
    config = {"configurable": {"thread_id": "campaign-unauthorized"}}

    graph.invoke(initial_state(), config=config)
    result = graph.invoke(Command(resume="approve"), config=config)

    assert "__interrupt__" in result
    state = graph.get_state(config).values
    assert state["current_state"] == "ERROR"
    assert state["failed_stage"] == "publish"
    assert "PermissionError" in state["error"]
    assert calls == []


def test_retry_recovers_failed_stage():
    calls = []
    attempts = {"create-campaign-content": 0}

    def flaky_executor(agent, skill, payload):
        if skill == "create-campaign-content":
            attempts[skill] += 1
            if attempts[skill] == 1:
                raise RuntimeError("temporary content failure")
        return stage_executor(agent, skill, payload)

    graph, _ = build(calls, execute_stage=flaky_executor)
    config = {"configurable": {"thread_id": "campaign-retry"}}

    first = graph.invoke(initial_state(), config=config)
    assert "__interrupt__" in first

    second = graph.invoke(Command(resume="retry"), config=config)
    assert "__interrupt__" in second
    assert attempts["create-campaign-content"] == 2


def test_duplicate_publish_prevention():
    calls = []
    graph, _ = build(calls)
    config = {"configurable": {"thread_id": "campaign-idempotent"}}
    state = initial_state()
    state["published"] = True
    state["publish_result"] = {"status": "published"}

    graph.invoke(state, config=config)
    final = graph.invoke(Command(resume="approve"), config=config)

    assert final["current_state"] == "COMPLETE"
    assert calls == []


def test_obsidian_persistence(tmp_path):
    calls = []
    persistence = ContentCampaignPersistence(ObsidianAdapter(tmp_path))
    graph, _ = build(calls, persistence=persistence)
    config = {"configurable": {"thread_id": "campaign-persist"}}

    graph.invoke(initial_state(), config=config)
    final = graph.invoke(
        Command(resume={"decision": "approve", "rationale": "Ready"}),
        config=config,
    )

    assert final["current_state"] == "COMPLETE"

    workspace = tmp_path / "Brand" / "Campaigns" / "campaign-1"
    assert (workspace / "campaign_brief.md").exists()
    assert (workspace / "publish_result.md").exists()
    assert (workspace / "campaign_learning.md").exists()
    assert (workspace / "decision-campaign.md").exists()
