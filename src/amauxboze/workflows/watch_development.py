from __future__ import annotations

from typing import Any, Callable, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from amauxboze.contracts import PolicyEngine, ToolRequest
from amauxboze.registries import AgentRegistry, SkillRegistry
from amauxboze.workflows.watch_persistence import WatchDevelopmentPersistence

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
    retry_count: int
    failed_stage: str
    recoverable: bool
    recovery_decision: str
    error: str


class WatchDevelopmentDependencies:
    def __init__(
        self,
        agents: AgentRegistry,
        skills: SkillRegistry,
        policy: PolicyEngine,
        execute_stage: StageExecutor,
        persistence: WatchDevelopmentPersistence | None = None,
    ):
        self.agents = agents
        self.skills = skills
        self.policy = policy
        self.execute_stage = execute_stage
        self.persistence = persistence


def _artifact(
    state: NewWatchDevelopmentState,
    artifact_type: str,
    agent_id: str,
    content: dict[str, Any],
):
    artifacts = list(state.get("artifacts", []))
    artifacts.append(
        {
            "artifact_type": artifact_type,
            "created_by": agent_id,
            "content": content,
        }
    )
    return artifacts


def build_new_watch_development_workflow(deps: WatchDevelopmentDependencies, *, checkpointer=None):
    graph = StateGraph(NewWatchDevelopmentState)

    def run(agent: str, skill: str, payload: dict[str, Any]) -> dict[str, Any]:
        deps.policy.authorize_skill(agent, skill)
        deps.skills.validate_input(skill, payload)
        result = deps.execute_stage(agent, skill, payload)
        deps.skills.validate_output(skill, result)
        return result

    def persist(
        state: NewWatchDevelopmentState,
        *,
        artifact_type: str,
        agent: str,
        skill: str,
        content: dict[str, Any],
    ) -> None:
        if deps.persistence is None:
            return
        deps.authorization.authorize_tool(agent, "obsidian", mode="write")
        deps.persistence.persist_artifact(
            workflow_id=state["workflow_id"],
            artifact_type=artifact_type,
            agent_id=agent,
            skill_id=skill,
            content=content,
        )

    def failure(state: NewWatchDevelopmentState, stage: str, exc: Exception):
        return {
            "current_state": "ERROR",
            "failed_stage": stage,
            "recoverable": True,
            "error": f"{type(exc).__name__}: {exc}",
            "retry_count": state.get("retry_count", 0),
        }

    def intent(state: NewWatchDevelopmentState):
        try:
            payload = {
                "founder_brief": state["founder_brief"],
                "constraints": state.get("constraints", []),
            }
            result = run("elena", "define-product-brief", payload)
            persist(state, artifact_type="product_brief", agent="elena", skill="define-product-brief", content=result)
            return {
                "product_brief": result,
                "current_state": "BRIEFED",
                "participating_agents": ["elena"],
                "artifacts": _artifact(state, "product_brief", "elena", result),
                "error": "",
            }
        except Exception as exc:
            return failure(state, "intent", exc)

    def research(state: NewWatchDevelopmentState):
        try:
            result = run("nora", "research-watch-opportunity", {"product_brief": state["product_brief"]})
            persist(state, artifact_type="evidence_pack", agent="nora", skill="research-watch-opportunity", content=result)
            return {
                "evidence_pack": result,
                "current_state": "RESEARCHED",
                "participating_agents": list(dict.fromkeys(state.get("participating_agents", []) + ["nora"])),
                "artifacts": _artifact(state, "evidence_pack", "nora", result),
                "error": "",
            }
        except Exception as exc:
            return failure(state, "research", exc)

    def concept(state: NewWatchDevelopmentState):
        try:
            result = run(
                "lucien",
                "design-watch-concept",
                {"product_brief": state["product_brief"], "evidence_pack": state["evidence_pack"]},
            )
            persist(state, artifact_type="product_concept", agent="lucien", skill="design-watch-concept", content=result)
            return {
                "product_concept": result,
                "current_state": "CONCEPTED",
                "participating_agents": list(dict.fromkeys(state.get("participating_agents", []) + ["lucien"])),
                "artifacts": _artifact(state, "product_concept", "lucien", result),
                "error": "",
            }
        except Exception as exc:
            return failure(state, "concept", exc)

    def brand_review(state: NewWatchDevelopmentState):
        try:
            result = run("elodie", "review-brand-fit", {"concept": state["product_concept"]})
            persist(state, artifact_type="brand_review", agent="elodie", skill="review-brand-fit", content=result)
            return {
                "brand_review": result,
                "current_state": "BRAND_REVIEWED",
                "participating_agents": list(dict.fromkeys(state.get("participating_agents", []) + ["elodie"])),
                "artifacts": _artifact(state, "brand_review", "elodie", result),
                "error": "",
            }
        except Exception as exc:
            return failure(state, "brand_review", exc)

    def commercial_review(state: NewWatchDevelopmentState):
        try:
            result = run(
                "marc",
                "review-commercial-fit",
                {"concept": state["product_concept"], "evidence_pack": state["evidence_pack"]},
            )
            persist(state, artifact_type="commercial_review", agent="marc", skill="review-commercial-fit", content=result)
            return {
                "commercial_review": result,
                "current_state": "COMMERCIAL_REVIEWED",
                "participating_agents": list(dict.fromkeys(state.get("participating_agents", []) + ["marc"])),
                "artifacts": _artifact(state, "commercial_review", "marc", result),
                "error": "",
            }
        except Exception as exc:
            return failure(state, "commercial_review", exc)

    def customer_review(state: NewWatchDevelopmentState):
        try:
            result = run("sophie", "review-customer-fit", {"concept": state["product_concept"]})
            persist(state, artifact_type="customer_review", agent="sophie", skill="review-customer-fit", content=result)
            return {
                "customer_review": result,
                "current_state": "CUSTOMER_REVIEWED",
                "participating_agents": list(dict.fromkeys(state.get("participating_agents", []) + ["sophie"])),
                "artifacts": _artifact(state, "customer_review", "sophie", result),
                "error": "",
            }
        except Exception as exc:
            return failure(state, "customer_review", exc)

    def integrate(state: NewWatchDevelopmentState):
        try:
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
            persist(
                state,
                artifact_type="integrated_recommendation",
                agent="elena",
                skill="integrate-watch-recommendation",
                content=result,
            )
            return {
                "integrated_recommendation": result,
                "current_state": "DECISION_READY",
                "artifacts": _artifact(state, "integrated_recommendation", "elena", result),
                "error": "",
            }
        except Exception as exc:
            return failure(state, "integrate", exc)

    def founder_gate(state: NewWatchDevelopmentState):
        response = interrupt(
            {
                "type": "founder_gate",
                "gate": "approve_for_spec",
                "workflow_id": state["workflow_id"],
                "allowed_decisions": ["approve", "revise", "hold", "reject"],
                "recommendation": state["integrated_recommendation"],
            }
        )
        decision = str(response.get("decision") if isinstance(response, dict) else response).lower()
        rationale = response.get("rationale", "") if isinstance(response, dict) else ""
        if decision not in {"approve", "revise", "hold", "reject"}:
            raise ValueError(f"Invalid founder decision: {decision}")
        if deps.persistence is not None:
            deps.persistence.persist_decision(
                workflow_id=state["workflow_id"],
                gate="approve_for_spec",
                decision=decision,
                rationale=rationale,
            )
        return {"founder_decision": decision}

    def route_founder_gate(state: NewWatchDevelopmentState):
        return state["founder_decision"]

    def mark_hold(state: NewWatchDevelopmentState):
        return {"current_state": "ON_HOLD"}

    def mark_rejected(state: NewWatchDevelopmentState):
        return {"current_state": "REJECTED"}

    def revision_concept(state: NewWatchDevelopmentState):
        return {"current_state": "REVISING_CONCEPT", "founder_decision": ""}

    def final_spec(state: NewWatchDevelopmentState):
        try:
            result = run(
                "lucien",
                "define-watch-spec",
                {"concept": state["product_concept"], "founder_decision": "approve"},
            )
            persist(state, artifact_type="final_specification", agent="lucien", skill="define-watch-spec", content=result)
            return {
                "final_specification": result,
                "current_state": "SPEC_COMPLETE",
                "artifacts": _artifact(state, "final_specification", "lucien", result),
                "error": "",
            }
        except Exception as exc:
            return failure(state, "final_spec", exc)

    def production_gate(state: NewWatchDevelopmentState):
        response = interrupt(
            {
                "type": "founder_gate",
                "gate": "production_approval",
                "workflow_id": state["workflow_id"],
                "allowed_decisions": ["approve", "revise", "cancel"],
                "specification": state["final_specification"],
            }
        )
        decision = str(response.get("decision") if isinstance(response, dict) else response).lower()
        rationale = response.get("rationale", "") if isinstance(response, dict) else ""
        if decision not in {"approve", "revise", "cancel"}:
            raise ValueError(f"Invalid production decision: {decision}")
        if deps.persistence is not None:
            deps.persistence.persist_decision(
                workflow_id=state["workflow_id"],
                gate="production_approval",
                decision=decision,
                rationale=rationale,
            )
        return {"production_decision": decision}

    def route_production_gate(state: NewWatchDevelopmentState):
        return state["production_decision"]

    def revision_spec(state: NewWatchDevelopmentState):
        return {"current_state": "REVISING_SPEC", "production_decision": ""}

    def approved(state: NewWatchDevelopmentState):
        return {"current_state": "APPROVED_FOR_PRODUCTION"}

    def cancelled(state: NewWatchDevelopmentState):
        return {"current_state": "CANCELLED"}

    def error_recovery(state: NewWatchDevelopmentState):
        response = interrupt(
            {
                "type": "error_recovery",
                "workflow_id": state["workflow_id"],
                "failed_stage": state["failed_stage"],
                "error": state["error"],
                "retry_count": state.get("retry_count", 0),
                "allowed_decisions": ["retry", "cancel"],
            }
        )
        decision = str(response.get("decision") if isinstance(response, dict) else response).lower()
        if decision not in {"retry", "cancel"}:
            raise ValueError(f"Invalid recovery decision: {decision}")
        return {
            "recovery_decision": decision,
            "retry_count": state.get("retry_count", 0) + (1 if decision == "retry" else 0),
        }

    def route_error_recovery(state: NewWatchDevelopmentState):
        if state["recovery_decision"] == "cancel":
            return "error_cancelled"
        return state["failed_stage"]

    def error_cancelled(state: NewWatchDevelopmentState):
        return {"current_state": "FAILED", "recoverable": False}

    def route_after_stage(state: NewWatchDevelopmentState):
        return "error_recovery" if state.get("current_state") == "ERROR" else "next"

    graph.add_node("intent", intent)
    graph.add_node("research", research)
    graph.add_node("concept", concept)
    graph.add_node("brand_review", brand_review)
    graph.add_node("commercial_review", commercial_review)
    graph.add_node("customer_review", customer_review)
    graph.add_node("integrate", integrate)
    graph.add_node("founder_gate", founder_gate)
    graph.add_node("revision_concept", revision_concept)
    graph.add_node("hold", mark_hold)
    graph.add_node("rejected", mark_rejected)
    graph.add_node("final_spec", final_spec)
    graph.add_node("production_gate", production_gate)
    graph.add_node("revision_spec", revision_spec)
    graph.add_node("approved", approved)
    graph.add_node("cancelled", cancelled)
    graph.add_node("error_recovery", error_recovery)
    graph.add_node("error_cancelled", error_cancelled)

    graph.add_edge(START, "intent")
    graph.add_conditional_edges("intent", route_after_stage, {"next": "research", "error_recovery": "error_recovery"})
    graph.add_conditional_edges("research", route_after_stage, {"next": "concept", "error_recovery": "error_recovery"})
    graph.add_conditional_edges("concept", route_after_stage, {"next": "brand_review", "error_recovery": "error_recovery"})
    graph.add_conditional_edges("brand_review", route_after_stage, {"next": "commercial_review", "error_recovery": "error_recovery"})
    graph.add_conditional_edges("commercial_review", route_after_stage, {"next": "customer_review", "error_recovery": "error_recovery"})
    graph.add_conditional_edges("customer_review", route_after_stage, {"next": "integrate", "error_recovery": "error_recovery"})
    graph.add_conditional_edges("integrate", route_after_stage, {"next": "founder_gate", "error_recovery": "error_recovery"})

    graph.add_conditional_edges(
        "founder_gate",
        route_founder_gate,
        {"approve": "final_spec", "revise": "revision_concept", "hold": "hold", "reject": "rejected"},
    )
    graph.add_edge("revision_concept", "concept")
    graph.add_edge("hold", END)
    graph.add_edge("rejected", END)

    graph.add_conditional_edges("final_spec", route_after_stage, {"next": "production_gate", "error_recovery": "error_recovery"})
    graph.add_conditional_edges(
        "production_gate",
        route_production_gate,
        {"approve": "approved", "revise": "revision_spec", "cancel": "cancelled"},
    )
    graph.add_edge("revision_spec", "final_spec")
    graph.add_edge("approved", END)
    graph.add_edge("cancelled", END)

    graph.add_conditional_edges(
        "error_recovery",
        route_error_recovery,
        {
            "intent": "intent",
            "research": "research",
            "concept": "concept",
            "brand_review": "brand_review",
            "commercial_review": "commercial_review",
            "customer_review": "customer_review",
            "integrate": "integrate",
            "final_spec": "final_spec",
            "error_cancelled": "error_cancelled",
        },
    )
    graph.add_edge("error_cancelled", END)

    return graph.compile(checkpointer=checkpointer if checkpointer is not None else MemorySaver())
