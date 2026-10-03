from pathlib import Path

from langgraph.types import Command

from amauxboze.adapters import ObsidianAdapter
from amauxboze.registries import AgentRegistry, AuthorizationService, SkillRegistry
from amauxboze.workflows.customer_feedback import (
    CustomerFeedbackDependencies,
    build_customer_feedback_workflow,
)
from amauxboze.workflows.customer_feedback_persistence import CustomerFeedbackPersistence


def stage_executor(agent, skill, payload):
    outputs = {
        "intake-feedback": {
            "source": payload.get("source", "review"),
            "observation": payload.get("raw_feedback", ""),
            "metadata": {},
        },
        "classify-feedback-signal": {
            "category": "product",
            "confidence": 0.95,
        },
        "assess-response-need": {
            "response_required": True,
            "consequential": False,
        },
        "draft-feedback-response": {
            "draft": "Thanks for your feedback.",
        },
        "detect-feedback-pattern": {
            "pattern_status": "isolated",
            "supporting_signals": [],
        },
        "assess-product-implication": {
            "impact": "low",
            "proposed_action": "monitor",
            "consequential": False,
        },
        "assess-brand-implication": {
            "impact": "medium",
            "proposed_action": "review messaging",
            "consequential": False,
        },
        "assess-commerce-implication": {
            "impact": "medium",
            "proposed_action": "review pricing",
            "consequential": True,
        },
        "assess-content-implication": {
            "impact": "low",
            "proposed_action": "clarify content",
            "consequential": False,
        },
        "prioritize-feedback-action": {
            "priority": "medium",
            "rationale": "Useful signal",
            "consequential": False,
        },
        "capture-feedback-learning": {
            "signal": "Customer feedback",
            "pattern": "isolated",
            "decision": "monitor",
            "action": "record",
        },
    }
    return outputs[skill]


def initial_state():
    return {
        "workflow_id": "feedback-1",
        "source": "review",
        "raw_feedback": "The crown feels too small.",
        "customer_context": {},
    }


def build(*, execute_stage=stage_executor, persistence=None):
    agents = AgentRegistry(Path("runtime/agents"))
    skills = SkillRegistry(Path("skills"))
    agents.load()
    skills.load()
    deps = CustomerFeedbackDependencies(
        skills=skills,
        authorization=AuthorizationService(agents, skills),
        execute_stage=execute_stage,
        persistence=persistence,
    )
    return build_customer_feedback_workflow(deps)


def test_isolated_feedback_path():
    graph = build()
    config = {"configurable": {"thread_id": "feedback-isolated"}}
    final = graph.invoke(initial_state(), config=config)
    assert final["current_state"] == "LEARNING_CAPTURED", final.get("error")
    assert final["pattern_analysis"]["pattern_status"] == "isolated"


def test_response_draft_without_send():
    graph = build()
    config = {"configurable": {"thread_id": "feedback-response"}}
    final = graph.invoke(initial_state(), config=config)
    assert final["response_draft"]["draft"]
    assert "customer_response_send" not in final


def test_product_implication_routing():
    graph = build()
    config = {"configurable": {"thread_id": "feedback-product"}}
    final = graph.invoke(initial_state(), config=config)
    assert "product" in final["functional_implications"]


def test_brand_implication_routing():
    def executor(agent, skill, payload):
        if skill == "classify-feedback-signal":
            return {"category": "brand", "confidence": 0.9}
        return stage_executor(agent, skill, payload)

    graph = build(execute_stage=executor)
    config = {"configurable": {"thread_id": "feedback-brand"}}
    final = graph.invoke(initial_state(), config=config)
    assert "brand" in final["functional_implications"]


def test_commerce_implication_routing_and_founder_gate():
    def executor(agent, skill, payload):
        if skill == "classify-feedback-signal":
            return {"category": "pricing", "confidence": 0.9}
        if skill == "prioritize-feedback-action":
            return {
                "priority": "high",
                "rationale": "Pricing change proposed",
                "consequential": True,
            }
        return stage_executor(agent, skill, payload)

    graph = build(execute_stage=executor)
    config = {"configurable": {"thread_id": "feedback-commerce"}}
    first = graph.invoke(initial_state(), config=config)
    assert "__interrupt__" in first

    final = graph.invoke(
        Command(resume={"decision": "approve", "rationale": "Proceed"}),
        config=config,
    )
    assert final["current_state"] == "LEARNING_CAPTURED"
    assert "commerce" in final["functional_implications"]
    assert final["founder_decision"] == "approve"


def test_content_implication_routing():
    def executor(agent, skill, payload):
        if skill == "classify-feedback-signal":
            return {"category": "communication", "confidence": 0.9}
        return stage_executor(agent, skill, payload)

    graph = build(execute_stage=executor)
    config = {"configurable": {"thread_id": "feedback-content"}}
    final = graph.invoke(initial_state(), config=config)
    assert "content" in final["functional_implications"]


def test_retry_recovers_failed_pattern_stage():
    attempts = {"detect-feedback-pattern": 0}

    def executor(agent, skill, payload):
        if skill == "detect-feedback-pattern":
            attempts[skill] += 1
            if attempts[skill] == 1:
                raise RuntimeError("temporary pattern failure")
        return stage_executor(agent, skill, payload)

    graph = build(execute_stage=executor)
    config = {"configurable": {"thread_id": "feedback-retry"}}

    first = graph.invoke(initial_state(), config=config)
    assert "__interrupt__" in first

    final = graph.invoke(Command(resume="retry"), config=config)
    assert final["current_state"] == "LEARNING_CAPTURED"
    assert attempts["detect-feedback-pattern"] == 2


def test_obsidian_persistence(tmp_path):
    persistence = CustomerFeedbackPersistence(ObsidianAdapter(tmp_path))
    graph = build(persistence=persistence)
    config = {"configurable": {"thread_id": "feedback-persist"}}
    final = graph.invoke(initial_state(), config=config)

    assert final["current_state"] == "LEARNING_CAPTURED"
    workspace = tmp_path / "Customers" / "Feedback" / "feedback-1"
    assert (workspace / "raw_observation.md").exists()
    assert (workspace / "classification.md").exists()
    assert (workspace / "learning_record.md").exists()
