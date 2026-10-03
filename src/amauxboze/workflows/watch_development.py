from __future__ import annotations

from typing import Any, Callable, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from amauxboze.registries import AgentRegistry, AuthorizationService, SkillRegistry

StageExecutor = Callable[[str, str, dict[str, Any]], dict[str, Any]]


class WatchArtifact(TypedDict):
    artifact_type: str
    created_by: str
    content: dict[str, Any]


class NewWatchDevelopmentState(TypedDict, total=False):
    workflow_id: str
    product_working_title: str
    founder_brief: str
    constraints: list[str]
    product_brief: dict[str, Any]
    evidence_pack: dict[str, Any]
    product_concept: dict[str, Any]
    brand_review: dict[str, Any]
    commercial_review: dict[str, Any]
    customer_review: dict[str, Any]
    integrated_recommendation: dict[str, Any]
    founder_decision: str
    final_specification: dict[str, Any]
    production_decision: str
    current_state: str
    participating_agents: list[str]
    artifacts: list[WatchArtifact]
    error: str


class WatchDevelopmentDependencies:
    def __init__(
        self,
        agents: AgentRegistry,
        skills: SkillRegistry,
        authorization: AuthorizationService,
        execute_stage: StageExecutor,
    ):
        self.agents = agents
        self.skills = skills
        self.authorization = authorization
        self.execute_stage = execute_stage


def _artifact(state: NewWatchDevelopmentState, artifact_type: str, agent_id: str, content: dict[str, Any]):
    artifacts = list(state.get("artifacts", []))
    artifacts.append(
        {
            "artifact_type": artifact_type,
            "created_by": agent_id,
            "content": content,
        }
    )
    return artifacts


def build_new_watch_development_workflow(deps: WatchDevelopmentDependencies):
    graph = StateGraph(NewWatchDevelopmentState)

    def run(agent: str, skill: str, payload: dict[str, Any]) -> dict[str, Any]:
        deps.authorization.authorize_skill(agent, skill)
        deps.skills.validate_input(skill, payload)
        result = deps.execute_stage(agent, skill, payload)
        deps.skills.validate_output(skill, result)
        return result

    def intent(state: NewWatchDevelopmentState):
        payload = {
            "founder_brief": state["founder_brief"],
            "constraints": state.get("constraints", []),
        }
        result = run("elena", "define-product-brief", payload)
        return {
            "product_brief": result,
            "current_state": "BRIEFED",
            "participating_agents": ["elena"],
            "artifacts": _artifact(state, "product_brief", "elena", result),
        }

    def research(state: NewWatchDevelopmentState):
        result = run("nora", "research-watch-opportunity", {"product_brief": state["product_brief"]})
        return {
            "evidence_pack": result,
            "current_state": "RESEARCHED",
            "participating_agents": list(dict.fromkeys(state.get("participating_agents", []) + ["nora"])),
            "artifacts": _artifact(state, "evidence_pack", "nora", result),
        }

    def concept(state: NewWatchDevelopmentState):
        result = run(
            "lucien",
            "design-watch-concept",
            {"product_brief": state["product_brief"], "evidence_pack": state["evidence_pack"]},
        )
        return {
            "product_concept": result,
            "current_state": "CONCEPTED",
            "participating_agents": list(dict.fromkeys(state.get("participating_agents", []) + ["lucien"])),
            "artifacts": _artifact(state, "product_concept", "lucien", result),
        }

    def brand_review(state: NewWatchDevelopmentState):
        result = run("elodie", "review-brand-fit", {"concept": state["product_concept"]})
        return {
            "brand_review": result,
            "current_state": "BRAND_REVIEWED",
            "participating_agents": list(dict.fromkeys(state.get("participating_agents", []) + ["elodie"])),
            "artifacts": _artifact(state, "brand_review", "elodie", result),
        }

    def commercial_review(state: NewWatchDevelopmentState):
        result = run(
            "marc",
            "review-commercial-fit",
            {"concept": state["product_concept"], "evidence_pack": state["evidence_pack"]},
        )
        return {
            "commercial_review": result,
            "current_state": "COMMERCIAL_REVIEWED",
            "participating_agents": list(dict.fromkeys(state.get("participating_agents", []) + ["marc"])),
            "artifacts": _artifact(state, "commercial_review", "marc", result),
        }

    def customer_review(state: NewWatchDevelopmentState):
        result = run("sophie", "review-customer-fit", {"concept": state["product_concept"]})
        return {
            "customer_review": result,
            "current_state": "CUSTOMER_REVIEWED",
            "participating_agents": list(dict.fromkeys(state.get("participating_agents", []) + ["sophie"])),
            "artifacts": _artifact(state, "customer_review", "sophie", result),
        }

    def integrate(state: NewWatchDevelopmentState):
        result = run(
            "elena",
            "integrate-watch-recommendation",
            {
                "concept": state["product_concept"],
                "brand_review": state["brand_review"],
                "commercial_review": state["commercial_review"],
                "customer_review": state["customer_review"],
            },
        )
        return {
            "integrated_recommendation": result,
            "current_state": "DECISION_READY",
            "artifacts": _artifact(state, "integrated_recommendation", "elena", result),
        }

    def founder_gate(state: NewWatchDevelopmentState):
        decision = str(
            interrupt(
                {
                    "type": "founder_gate",
                    "gate": "approve_for_spec",
                    "workflow_id": state["workflow_id"],
                    "allowed_decisions": ["approve", "revise", "hold", "reject"],
                    "recommendation": state["integrated_recommendation"],
                }
            )
        ).lower()
        if decision not in {"approve", "revise", "hold", "reject"}:
            raise ValueError(f"Invalid founder decision: {decision}")
        return {"founder_decision": decision}

    def route_founder_gate(state: NewWatchDevelopmentState):
        return state["founder_decision"]

    def mark_hold(state: NewWatchDevelopmentState):
        return {"current_state": "ON_HOLD"}

    def mark_rejected(state: NewWatchDevelopmentState):
        return {"current_state": "REJECTED"}

    def revision(state: NewWatchDevelopmentState):
        return {"current_state": "REVISION_REQUIRED"}

    def final_spec(state: NewWatchDevelopmentState):
        result = run(
            "lucien",
            "define-watch-spec",
            {"concept": state["product_concept"], "founder_decision": state["founder_decision"]},
        )
        return {
            "final_specification": result,
            "current_state": "SPEC_COMPLETE",
            "artifacts": _artifact(state, "final_specification", "lucien", result),
        }

    def production_gate(state: NewWatchDevelopmentState):
        decision = str(
            interrupt(
                {
                    "type": "founder_gate",
                    "gate": "production_approval",
                    "workflow_id": state["workflow_id"],
                    "allowed_decisions": ["approve", "revise", "cancel"],
                    "specification": state["final_specification"],
                }
            )
        ).lower()
        if decision not in {"approve", "revise", "cancel"}:
            raise ValueError(f"Invalid production decision: {decision}")
        return {"production_decision": decision}

    def route_production_gate(state: NewWatchDevelopmentState):
        return state["production_decision"]

    def approved(state: NewWatchDevelopmentState):
        return {"current_state": "APPROVED_FOR_PRODUCTION"}

    def cancelled(state: NewWatchDevelopmentState):
        return {"current_state": "CANCELLED"}

    graph.add_node("intent", intent)
    graph.add_node("research", research)
    graph.add_node("concept", concept)
    graph.add_node("brand_review", brand_review)
    graph.add_node("commercial_review", commercial_review)
    graph.add_node("customer_review", customer_review)
    graph.add_node("integrate", integrate)
    graph.add_node("founder_gate", founder_gate)
    graph.add_node("revision", revision)
    graph.add_node("hold", mark_hold)
    graph.add_node("rejected", mark_rejected)
    graph.add_node("final_spec", final_spec)
    graph.add_node("production_gate", production_gate)
    graph.add_node("approved", approved)
    graph.add_node("cancelled", cancelled)

    graph.add_edge(START, "intent")
    graph.add_edge("intent", "research")
    graph.add_edge("research", "concept")
    graph.add_edge("concept", "brand_review")
    graph.add_edge("brand_review", "commercial_review")
    graph.add_edge("commercial_review", "customer_review")
    graph.add_edge("customer_review", "integrate")
    graph.add_edge("integrate", "founder_gate")

    graph.add_conditional_edges(
        "founder_gate",
        route_founder_gate,
        {
            "approve": "final_spec",
            "revise": "revision",
            "hold": "hold",
            "reject": "rejected",
        },
    )
    graph.add_edge("revision", END)
    graph.add_edge("hold", END)
    graph.add_edge("rejected", END)

    graph.add_edge("final_spec", "production_gate")
    graph.add_conditional_edges(
        "production_gate",
        route_production_gate,
        {
            "approve": "approved",
            "revise": "revision",
            "cancel": "cancelled",
        },
    )
    graph.add_edge("approved", END)
    graph.add_edge("cancelled", END)

    return graph.compile(checkpointer=MemorySaver())
