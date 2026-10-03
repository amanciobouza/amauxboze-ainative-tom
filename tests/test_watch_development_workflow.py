from pathlib import Path

from langgraph.types import Command

from amauxboze.registries import AgentRegistry, AuthorizationService, SkillRegistry
from amauxboze.workflows.watch_development import (
    WatchDevelopmentDependencies,
    build_new_watch_development_workflow,
)


def stage_executor(agent, skill, payload):
    outputs = {
        "define-product-brief": {
            "objective": "Create a new watch",
            "constraints": payload.get("constraints", []),
            "open_questions": [],
        },
        "research-watch-opportunity": {
            "observations": ["Microbrand category is competitive"],
            "opportunities": ["Distinct narrative"],
            "risks": ["Price sensitivity"],
        },
        "design-watch-concept": {
            "concept_name": "Project Purpose",
            "movement": "NH35",
            "case_direction": "40 mm steel",
            "dial_direction": "Purpose-led dial",
            "feasibility_notes": ["Uses known components"],
        },
        "review-brand-fit": {
            "fit": "strong",
            "strengths": ["Purpose narrative"],
            "risks": [],
            "narrative_directions": ["Power → Control → Purpose"],
        },
        "review-commercial-fit": {
            "pricing_view": "Within target band",
            "commercial_risks": [],
            "positioning_implications": ["Keep proposition clear"],
        },
        "review-customer-fit": {
            "relevance": "Relevant to target customer",
            "objections": [],
            "misunderstandings": [],
        },
        "integrate-watch-recommendation": {
            "summary": "Proceed to detailed specification.",
            "tradeoffs": ["Narrative vs simplicity"],
            "recommendation_options": ["approve", "revise"],
        },
        "define-watch-spec": {
            "movement": "NH35",
            "case": "40 mm 316L",
            "dial": "Purpose dial",
            "hands": "Applied steel hands",
            "crystal": "Sapphire",
            "water_resistance": "50 m",
            "open_assumptions": [],
        },
    }
    return outputs[skill]


def build():
    agents = AgentRegistry(Path("runtime/agents"))
    skills = SkillRegistry(Path("skills"))
    agents.load()
    skills.load()
    deps = WatchDevelopmentDependencies(
        agents=agents,
        skills=skills,
        authorization=AuthorizationService(agents, skills),
        execute_stage=stage_executor,
    )
    return build_new_watch_development_workflow(deps)


def test_happy_path_through_both_founder_gates():
    graph = build()
    config = {"configurable": {"thread_id": "watch-happy"}}

    first = graph.invoke(
        {
            "workflow_id": "wf-watch-1",
            "founder_brief": "Create a purpose-led mechanical watch.",
            "constraints": ["Target price CHF 300-350"],
        },
        config=config,
    )
    assert "__interrupt__" in first

    second = graph.invoke(Command(resume="approve"), config=config)
    assert "__interrupt__" in second

    final = graph.invoke(Command(resume="approve"), config=config)
    assert final["current_state"] == "APPROVED_FOR_PRODUCTION"
    assert final["final_specification"]["movement"] == "NH35"


def test_founder_reject_path():
    graph = build()
    config = {"configurable": {"thread_id": "watch-reject"}}
    graph.invoke(
        {"workflow_id": "wf-watch-2", "founder_brief": "Test concept", "constraints": []},
        config=config,
    )
    final = graph.invoke(Command(resume="reject"), config=config)
    assert final["current_state"] == "REJECTED"


def test_founder_hold_path():
    graph = build()
    config = {"configurable": {"thread_id": "watch-hold"}}
    graph.invoke(
        {"workflow_id": "wf-watch-3", "founder_brief": "Test concept", "constraints": []},
        config=config,
    )
    final = graph.invoke(Command(resume="hold"), config=config)
    assert final["current_state"] == "ON_HOLD"


def test_production_cancel_path():
    graph = build()
    config = {"configurable": {"thread_id": "watch-cancel"}}
    graph.invoke(
        {"workflow_id": "wf-watch-4", "founder_brief": "Test concept", "constraints": []},
        config=config,
    )
    graph.invoke(Command(resume="approve"), config=config)
    final = graph.invoke(Command(resume="cancel"), config=config)
    assert final["current_state"] == "CANCELLED"
