from pathlib import Path

from langgraph.types import Command

from amauxboze.registries import AgentRegistry, AuthorizationService, SkillRegistry
from amauxboze.workflows.product_launch import (
    ProductLaunchDependencies,
    build_product_launch_workflow,
)


def stage_executor(agent, skill, payload):
    outputs = {
        "define-launch-brief": {
            "objective": "Launch new watch",
            "milestones": ["prepare", "approve", "launch"],
            "dependencies": [],
            "open_decisions": [],
        },
        "create-product-truth-pack": {
            "approved_claims": ["40 mm steel case"],
            "prohibited_claims": ["Swiss Made"],
            "sku_facts": ["SKU-001"],
        },
        "create-launch-messaging": {
            "core_message": "Purpose matters.",
            "supporting_messages": ["Mechanical watch"],
            "narrative_frame": "Power → Control → Purpose",
        },
        "prepare-commercial-launch": {
            "pricing_view": "CHF 349",
            "shopify_draft": {"title": "Test Watch"},
            "conversion_plan": ["product page"],
        },
        "create-launch-content": {
            "tiktok": ["video"],
            "instagram": ["post"],
            "pinterest": ["pin"],
            "x": ["post"],
            "calendar": ["day 1"],
        },
        "prepare-customer-readiness": {
            "faq": ["What movement?"],
            "objections": [],
            "support_guidance": ["Answer from truth pack"],
        },
        "check-launch-market-context": {
            "changes": [],
            "timing_risks": [],
            "notes": [],
        },
        "integrate-launch-readiness": {
            "summary": "Ready",
            "blockers": [],
            "required_approvals": ["founder"],
        },
        "capture-launch-learning": {
            "what_worked": ["Clear message"],
            "what_did_not": [],
            "next_experiment": "Test a second hook",
        },
    }
    return outputs[skill]


def build(activation_calls):
    agents = AgentRegistry(Path("runtime/agents"))
    skills = SkillRegistry(Path("skills"))
    agents.load()
    skills.load()

    def activation(payload):
        activation_calls.append(payload)
        return {"status": "activated"}

    deps = ProductLaunchDependencies(
        skills=skills,
        authorization=AuthorizationService(agents, skills),
        execute_stage=stage_executor,
        execute_activation=activation,
    )
    return build_product_launch_workflow(deps)


def initial_state():
    return {
        "workflow_id": "launch-1",
        "product_id": "watch-1",
        "approved_specification": True,
        "product_specification": {"case": "40 mm steel"},
        "launch_objective": "Launch the watch",
    }


def test_missing_approved_spec_rejected():
    calls = []
    graph = build(calls)
    config = {"configurable": {"thread_id": "launch-missing"}}
    state = initial_state()
    state["approved_specification"] = False

    final = graph.invoke(state, config=config)
    assert final["current_state"] == "REJECTED_MISSING_APPROVED_SPEC"
    assert calls == []


def test_happy_path_activates_once_and_completes():
    calls = []
    graph = build(calls)
    config = {"configurable": {"thread_id": "launch-happy"}}

    first = graph.invoke(initial_state(), config=config)
    assert "__interrupt__" in first

    final = graph.invoke(Command(resume="approve"), config=config)
    assert final["current_state"] == "COMPLETE"
    assert final["activation_executed"] is True
    assert len(calls) == 1


def test_hold_path():
    calls = []
    graph = build(calls)
    config = {"configurable": {"thread_id": "launch-hold"}}
    graph.invoke(initial_state(), config=config)
    final = graph.invoke(Command(resume="hold"), config=config)
    assert final["current_state"] == "ON_HOLD"
    assert calls == []


def test_cancel_path():
    calls = []
    graph = build(calls)
    config = {"configurable": {"thread_id": "launch-cancel"}}
    graph.invoke(initial_state(), config=config)
    final = graph.invoke(Command(resume="cancel"), config=config)
    assert final["current_state"] == "CANCELLED"
    assert calls == []


def test_revision_returns_to_preparation_and_gates_again():
    calls = []
    graph = build(calls)
    config = {"configurable": {"thread_id": "launch-revise"}}
    graph.invoke(initial_state(), config=config)
    second = graph.invoke(Command(resume="revise"), config=config)
    assert "__interrupt__" in second
    assert calls == []
