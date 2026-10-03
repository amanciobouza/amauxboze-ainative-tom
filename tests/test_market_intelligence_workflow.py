from pathlib import Path

from langgraph.types import Command

from amauxboze.adapters import ObsidianAdapter
from amauxboze.registries import AgentRegistry, AuthorizationService, SkillRegistry
from amauxboze.workflows.market_intelligence import (
    MarketIntelligenceDependencies,
    build_market_intelligence_workflow,
)
from amauxboze.workflows.market_intelligence_persistence import MarketIntelligencePersistence


def stage_executor(agent, skill, payload):
    outputs = {
        "define-research-question": {
            "research_question": "How is the microbrand watch market changing?",
            "scope": ["pricing", "positioning"],
            "unknowns": ["future demand"],
        },
        "collect-market-evidence": {
            "sources": ["source-a", "source-b"],
            "evidence_items": ["prices rising", "discounting increasing"],
        },
        "capture-market-observations": {
            "observations": [
                {
                    "statement": "Some competitors raised prices.",
                    "source": "source-a",
                    "observed_date": "2026-10-03",
                    "geography": "Global",
                    "confidence": "high",
                    "tags": ["pricing"],
                }
            ]
        },
        "detect-market-change": {
            "signals": ["premiumization"],
            "contradictions": ["discounting also increased"],
            "unknowns": ["durability of trend"],
        },
        "interpret-product-impact": {
            "implications": ["protect product distinctiveness"],
            "risks": ["feature inflation"],
            "opportunities": ["clearer product architecture"],
        },
        "interpret-brand-impact": {
            "implications": ["avoid luxury cliché"],
            "risks": ["status-copy convergence"],
            "opportunities": ["purpose positioning"],
        },
        "interpret-commercial-impact": {
            "implications": ["price discipline matters"],
            "risks": ["conversion pressure"],
            "opportunities": ["value framing"],
        },
        "interpret-customer-impact": {
            "implications": ["clarity matters"],
            "risks": ["price confusion"],
            "opportunities": ["education"],
        },
        "synthesize-strategic-insight": {
            "what_is_known": ["pricing is moving"],
            "what_is_uncertain": ["trend durability"],
            "why_it_matters": "Positioning must stay distinct.",
            "options": ["act", "monitor"],
        },
        "prepare-strategic-decision": {
            "summary": "Pricing and positioning are shifting.",
            "decision_options": ["act", "investigate_further", "monitor", "archive"],
            "follow_up_conditions": ["recheck in 30 days"],
        },
        "update-intelligence-knowledge": {
            "status": "stored",
            "stored_items": ["insight", "decision"],
        },
    }
    return outputs[skill]


def initial_state():
    return {
        "workflow_id": "intel-1",
        "watch_topic": "Microbrand market",
        "geography": "Global",
    }


def build(*, execute_stage=stage_executor, persistence=None):
    agents = AgentRegistry(Path("runtime/agents"))
    skills = SkillRegistry(Path("skills"))
    agents.load()
    skills.load()
    deps = MarketIntelligenceDependencies(
        skills=skills,
        authorization=AuthorizationService(agents, skills),
        execute_stage=execute_stage,
        persistence=persistence,
    )
    return build_market_intelligence_workflow(deps)


def test_evidence_backed_observation_path():
    graph = build()
    config = {"configurable": {"thread_id": "intel-evidence"}}

    first = graph.invoke(initial_state(), config=config)
    assert "__interrupt__" in first
    state = graph.get_state(config).values

    obs = state["observations"]["observations"][0]
    assert obs["source"] == "source-a"
    assert obs["observed_date"] == "2026-10-03"
    assert obs["geography"] == "Global"
    assert obs["confidence"] == "high"


def test_observation_remains_unchanged_after_interpretation():
    graph = build()
    config = {"configurable": {"thread_id": "intel-immutable"}}
    graph.invoke(initial_state(), config=config)
    state = graph.get_state(config).values

    assert state["observations"] == state["observations_snapshot"]


def test_contradictory_evidence_is_preserved():
    graph = build()
    config = {"configurable": {"thread_id": "intel-contradiction"}}
    graph.invoke(initial_state(), config=config)
    state = graph.get_state(config).values

    assert "discounting also increased" in state["pattern_analysis"]["contradictions"]


def test_functional_interpretations_remain_separate():
    graph = build()
    config = {"configurable": {"thread_id": "intel-separate"}}
    graph.invoke(initial_state(), config=config)
    state = graph.get_state(config).values

    assert "product_interpretation" in state
    assert "brand_interpretation" in state
    assert "commercial_interpretation" in state
    assert "customer_interpretation" in state
    assert state["product_interpretation"] != state["brand_interpretation"]


def test_all_founder_outcomes():
    for decision in ["act", "investigate_further", "monitor", "archive"]:
        graph = build()
        config = {"configurable": {"thread_id": f"intel-{decision}"}}
        graph.invoke(initial_state(), config=config)
        final = graph.invoke(
            Command(resume={"decision": decision, "rationale": "Test"}),
            config=config,
        )
        assert final["current_state"] == "KNOWLEDGE_UPDATED"
        assert final["founder_decision"] == decision


def test_retry_recovers_failed_synthesis():
    attempts = {"synthesize-strategic-insight": 0}

    def executor(agent, skill, payload):
        if skill == "synthesize-strategic-insight":
            attempts[skill] += 1
            if attempts[skill] == 1:
                raise RuntimeError("temporary synthesis failure")
        return stage_executor(agent, skill, payload)

    graph = build(execute_stage=executor)
    config = {"configurable": {"thread_id": "intel-retry"}}

    first = graph.invoke(initial_state(), config=config)
    assert "__interrupt__" in first

    second = graph.invoke(Command(resume="retry"), config=config)
    assert "__interrupt__" in second
    assert attempts["synthesize-strategic-insight"] == 2


def test_historical_persistence_preserves_multiple_artifacts(tmp_path):
    persistence = MarketIntelligencePersistence(ObsidianAdapter(tmp_path))
    graph = build(persistence=persistence)
    config = {"configurable": {"thread_id": "intel-history"}}

    graph.invoke(initial_state(), config=config)
    final = graph.invoke(
        Command(resume={"decision": "monitor", "rationale": "Need more data"}),
        config=config,
    )

    assert final["current_state"] == "KNOWLEDGE_UPDATED"

    workspace = tmp_path / "Research" / "Intelligence" / "intel-1"
    files = list(workspace.glob("*.md"))
    names = [p.name for p in files]
    assert len(files) >= 8
    assert any("observations" in name for name in names)
    assert any("strategic_insight" in name for name in names)
    assert any("founder-decision" in name for name in names)
