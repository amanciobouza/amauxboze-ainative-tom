from __future__ import annotations

from typing import Any, Callable, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from amauxboze.contracts import PolicyEngine, ToolRequest
from amauxboze.registries import SkillRegistry
from amauxboze.workflows.customer_feedback_persistence import CustomerFeedbackPersistence

StageExecutor = Callable[[str, str, dict[str, Any]], dict[str, Any]]


class CustomerFeedbackState(TypedDict, total=False):
    workflow_id: str
    source: str
    raw_feedback: str
    customer_context: dict[str, Any]
    observation: dict[str, Any]
    classification: dict[str, Any]
    response_need: dict[str, Any]
    response_draft: dict[str, Any]
    pattern_analysis: dict[str, Any]
    functional_implications: dict[str, Any]
    prioritization: dict[str, Any]
    founder_decision: str
    learning_record: dict[str, Any]
    current_state: str
    retry_count: int
    failed_stage: str
    recoverable: bool
    recovery_decision: str
    error: str


class CustomerFeedbackDependencies:
    def __init__(
        self,
        skills: SkillRegistry,
        policy: PolicyEngine,
        execute_stage: StageExecutor,
        persistence: CustomerFeedbackPersistence | None = None,
    ):
        self.skills = skills
        self.policy = policy
        self.execute_stage = execute_stage
        self.persistence = persistence


def build_customer_feedback_workflow(deps: CustomerFeedbackDependencies):
    graph = StateGraph(CustomerFeedbackState)

    def run(agent: str, skill: str, payload: dict[str, Any]) -> dict[str, Any]:
        deps.policy.authorize_skill(agent, skill)
        deps.skills.validate_input(skill, payload)
        result = deps.execute_stage(agent, skill, payload)
        deps.skills.validate_output(skill, result)
        return result

    def persist(state: CustomerFeedbackState, artifact_type: str, agent: str, skill: str, content: dict[str, Any]):
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

    def failure(state: CustomerFeedbackState, stage: str, exc: Exception):
        return {
            "current_state": "ERROR",
            "failed_stage": stage,
            "recoverable": True,
            "error": f"{type(exc).__name__}: {exc}",
            "retry_count": state.get("retry_count", 0),
        }

    def intake(state: CustomerFeedbackState):
        try:
            result = run(
                "sophie",
                "intake-feedback",
                {
                    "source": state["source"],
                    "raw_feedback": state["raw_feedback"],
                    "customer_context": state.get("customer_context", {}),
                },
            )
            persist(state, "raw_observation", "sophie", "intake-feedback", result)
            return {"observation": result, "current_state": "RECEIVED", "error": ""}
        except Exception as exc:
            return failure(state, "intake", exc)

    def classify(state: CustomerFeedbackState):
        try:
            result = run("sophie", "classify-feedback-signal", {"observation": state["observation"]})
            persist(state, "classification", "sophie", "classify-feedback-signal", result)
            return {"classification": result, "current_state": "CLASSIFIED", "error": ""}
        except Exception as exc:
            return failure(state, "classify", exc)

    def response_need(state: CustomerFeedbackState):
        try:
            result = run(
                "sophie",
                "assess-response-need",
                {"observation": state["observation"], "classification": state["classification"]},
            )
            persist(state, "response_need", "sophie", "assess-response-need", result)
            return {"response_need": result, "current_state": "RESPONSE_ASSESSED", "error": ""}
        except Exception as exc:
            return failure(state, "response_need", exc)

    def route_response(state: CustomerFeedbackState):
        if state.get("current_state") == "ERROR":
            return "error_recovery"
        return "draft" if state["response_need"]["response_required"] else "skip"

    def draft_response(state: CustomerFeedbackState):
        try:
            result = run(
                "sophie",
                "draft-feedback-response",
                {"observation": state["observation"], "classification": state["classification"]},
            )
            persist(state, "response_draft", "sophie", "draft-feedback-response", result)
            return {"response_draft": result, "current_state": "RESPONSE_DRAFTED", "error": ""}
        except Exception as exc:
            return failure(state, "draft_response", exc)

    def pattern(state: CustomerFeedbackState):
        try:
            result = run(
                "nora",
                "detect-feedback-pattern",
                {"observation": state["observation"], "classification": state["classification"]},
            )
            persist(state, "pattern_analysis", "nora", "detect-feedback-pattern", result)
            return {"pattern_analysis": result, "current_state": "ANALYZED", "error": ""}
        except Exception as exc:
            return failure(state, "pattern", exc)

    def implication(state: CustomerFeedbackState):
        try:
            category = state["classification"]["category"].lower()
            if category in {"product quality", "design", "fit / comfort", "product"}:
                agent, skill, key = "lucien", "assess-product-implication", "product"
            elif category in {"brand perception", "brand"}:
                agent, skill, key = "elodie", "assess-brand-implication", "brand"
            elif category in {"pricing", "shipping", "website / checkout", "commerce"}:
                agent, skill, key = "marc", "assess-commerce-implication", "commerce"
            else:
                agent, skill, key = "maya", "assess-content-implication", "content"

            result = run(
                agent,
                skill,
                {"classification": state["classification"], "pattern_analysis": state["pattern_analysis"]},
            )
            wrapper = {key: result}
            persist(state, "functional_implications", agent, skill, wrapper)
            return {"functional_implications": wrapper, "current_state": "FUNCTION_REVIEWED", "error": ""}
        except Exception as exc:
            return failure(state, "implication", exc)

    def prioritize(state: CustomerFeedbackState):
        try:
            result = run(
                "elena",
                "prioritize-feedback-action",
                {"functional_implications": state["functional_implications"]},
            )
            persist(state, "prioritization", "elena", "prioritize-feedback-action", result)
            return {"prioritization": result, "current_state": "PRIORITIZED", "error": ""}
        except Exception as exc:
            return failure(state, "prioritize", exc)

    def consequential_route(state: CustomerFeedbackState):
        if state.get("current_state") == "ERROR":
            return "error_recovery"
        return "founder_gate" if state["prioritization"]["consequential"] else "learning"

    def founder_gate(state: CustomerFeedbackState):
        response = interrupt({
            "type": "founder_gate",
            "gate": "feedback_action",
            "workflow_id": state["workflow_id"],
            "allowed_decisions": ["approve", "revise", "reject"],
            "prioritization": state["prioritization"],
        })
        decision = str(response.get("decision") if isinstance(response, dict) else response).lower()
        rationale = response.get("rationale", "") if isinstance(response, dict) else ""
        if decision not in {"approve", "revise", "reject"}:
            raise ValueError(f"Invalid founder decision: {decision}")
        if deps.persistence is not None:
            deps.persistence.persist_decision(workflow_id=state["workflow_id"], decision=decision, rationale=rationale)
        return {"founder_decision": decision}

    def route_founder(state: CustomerFeedbackState):
        return state["founder_decision"]

    def revise(state: CustomerFeedbackState):
        return {"current_state": "REVISION_REQUIRED", "founder_decision": ""}

    def reject(state: CustomerFeedbackState):
        return {"current_state": "REJECTED"}

    def learning(state: CustomerFeedbackState):
        try:
            result = run(
                "sophie",
                "capture-feedback-learning",
                {
                    "observation": state["observation"],
                    "classification": state["classification"],
                    "pattern_analysis": state["pattern_analysis"],
                    "prioritization": state["prioritization"],
                    "founder_decision": state.get("founder_decision", "not_required"),
                },
            )
            persist(state, "learning_record", "sophie", "capture-feedback-learning", result)
            return {"learning_record": result, "current_state": "LEARNING_CAPTURED", "error": ""}
        except Exception as exc:
            return failure(state, "learning", exc)

    def route_after_stage(state: CustomerFeedbackState):
        return "error_recovery" if state.get("current_state") == "ERROR" else "next"

    def error_recovery(state: CustomerFeedbackState):
        response = interrupt({
            "type": "error_recovery",
            "workflow_id": state["workflow_id"],
            "failed_stage": state["failed_stage"],
            "error": state["error"],
            "retry_count": state.get("retry_count", 0),
            "allowed_decisions": ["retry", "cancel"],
        })
        decision = str(response.get("decision") if isinstance(response, dict) else response).lower()
        if decision not in {"retry", "cancel"}:
            raise ValueError(f"Invalid recovery decision: {decision}")
        return {
            "recovery_decision": decision,
            "retry_count": state.get("retry_count", 0) + (1 if decision == "retry" else 0),
        }

    def route_error(state: CustomerFeedbackState):
        if state["recovery_decision"] == "cancel":
            return "error_cancelled"
        return state["failed_stage"]

    def error_cancelled(state: CustomerFeedbackState):
        return {"current_state": "FAILED", "recoverable": False}

    for name, fn in [
        ("intake", intake),
        ("classify", classify),
        ("response_need", response_need),
        ("draft_response", draft_response),
        ("pattern", pattern),
        ("implication", implication),
        ("prioritize", prioritize),
        ("founder_gate", founder_gate),
        ("revise", revise),
        ("reject", reject),
        ("learning", learning),
        ("error_recovery", error_recovery),
        ("error_cancelled", error_cancelled),
    ]:
        graph.add_node(name, fn)

    graph.add_edge(START, "intake")
    graph.add_conditional_edges("intake", route_after_stage, {"next": "classify", "error_recovery": "error_recovery"})
    graph.add_conditional_edges("classify", route_after_stage, {"next": "response_need", "error_recovery": "error_recovery"})
    graph.add_conditional_edges(
        "response_need",
        route_response,
        {"draft": "draft_response", "skip": "pattern", "error_recovery": "error_recovery"},
    )
    graph.add_conditional_edges("draft_response", route_after_stage, {"next": "pattern", "error_recovery": "error_recovery"})
    graph.add_conditional_edges("pattern", route_after_stage, {"next": "implication", "error_recovery": "error_recovery"})
    graph.add_conditional_edges("implication", route_after_stage, {"next": "prioritize", "error_recovery": "error_recovery"})
    graph.add_conditional_edges(
        "prioritize",
        consequential_route,
        {"founder_gate": "founder_gate", "learning": "learning", "error_recovery": "error_recovery"},
    )

    graph.add_conditional_edges(
        "founder_gate",
        route_founder,
        {"approve": "learning", "revise": "revise", "reject": "reject"},
    )
    graph.add_edge("revise", "implication")
    graph.add_edge("reject", END)
    graph.add_conditional_edges("learning", route_after_stage, {"next": END, "error_recovery": "error_recovery"})

    graph.add_conditional_edges(
        "error_recovery",
        route_error,
        {
            "intake": "intake",
            "classify": "classify",
            "response_need": "response_need",
            "draft_response": "draft_response",
            "pattern": "pattern",
            "implication": "implication",
            "prioritize": "prioritize",
            "learning": "learning",
            "error_cancelled": "error_cancelled",
        },
    )
    graph.add_edge("error_cancelled", END)

    return graph.compile(checkpointer=MemorySaver())
