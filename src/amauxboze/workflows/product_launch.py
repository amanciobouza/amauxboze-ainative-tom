from __future__ import annotations

from typing import Any, Callable, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from amauxboze.contracts import PolicyEngine, ToolRequest
from amauxboze.registries import SkillRegistry
from amauxboze.workflows.product_launch_persistence import ProductLaunchPersistence

StageExecutor = Callable[[str, str, dict[str, Any]], dict[str, Any]]
ActivationExecutor = Callable[[dict[str, Any]], dict[str, Any]]


class ProductLaunchState(TypedDict, total=False):
    workflow_id: str
    product_id: str
    product_specification: dict[str, Any]
    approved_specification: bool
    launch_objective: str
    launch_brief: dict[str, Any]
    product_truth_pack: dict[str, Any]
    messaging_framework: dict[str, Any]
    commercial_setup: dict[str, Any]
    content_plan: dict[str, Any]
    support_pack: dict[str, Any]
    market_context: dict[str, Any]
    launch_readiness: dict[str, Any]
    founder_decision: str
    activation_result: dict[str, Any]
    performance_snapshot: dict[str, Any]
    launch_learning: dict[str, Any]
    current_state: str
    activation_key: str
    activation_executed: bool
    retry_count: int
    failed_stage: str
    recoverable: bool
    recovery_decision: str
    error: str


class ProductLaunchDependencies:
    def __init__(
        self,
        skills: SkillRegistry,
        policy: PolicyEngine,
        execute_stage: StageExecutor,
        execute_activation: ActivationExecutor,
        persistence: ProductLaunchPersistence | None = None,
    ):
        self.skills = skills
        self.policy = policy
        self.execute_stage = execute_stage
        self.execute_activation = execute_activation
        self.persistence = persistence


def build_product_launch_workflow(deps: ProductLaunchDependencies):
    graph = StateGraph(ProductLaunchState)

    def run(agent: str, skill: str, payload: dict[str, Any]) -> dict[str, Any]:
        deps.policy.authorize_skill(agent, skill)
        deps.skills.validate_input(skill, payload)
        result = deps.execute_stage(agent, skill, payload)
        deps.skills.validate_output(skill, result)
        return result

    def persist_artifact(state: ProductLaunchState, *, artifact_type: str, agent: str, skill: str, content: dict[str, Any]):
        if deps.persistence is None:
            return
        deps.policy.authorize_tool(ToolRequest(agent_id=agent, skill_id=skill, tool_name="obsidian", mode="write"))
        deps.persistence.persist_artifact(
            workflow_id=state["workflow_id"],
            artifact_type=artifact_type,
            agent_id=agent,
            skill_id=skill,
            content=content,
        )

    def failure(state: ProductLaunchState, stage: str, exc: Exception):
        return {
            "current_state": "ERROR",
            "failed_stage": stage,
            "recoverable": True,
            "error": f"{type(exc).__name__}: {exc}",
            "retry_count": state.get("retry_count", 0),
        }

    def validate_spec(state: ProductLaunchState):
        if not state.get("approved_specification"):
            return {
                "current_state": "REJECTED_MISSING_APPROVED_SPEC",
                "error": "Product Launch requires an approved product specification.",
            }
        return {"current_state": "SPEC_VALIDATED"}

    def route_spec(state: ProductLaunchState):
        return "valid" if state["current_state"] == "SPEC_VALIDATED" else "invalid"

    def launch_brief(state: ProductLaunchState):
        try:
            result = run(
                "elena",
                "define-launch-brief",
                {
                    "product_specification": state["product_specification"],
                    "launch_objective": state["launch_objective"],
                },
            )
            persist_artifact(state, artifact_type="launch_brief", agent="elena", skill="define-launch-brief", content=result)
            return {"launch_brief": result, "current_state": "LAUNCH_BRIEF_READY", "error": ""}
        except Exception as exc:
            return failure(state, "launch_brief", exc)

    def truth_pack(state: ProductLaunchState):
        try:
            result = run(
                "lucien",
                "create-product-truth-pack",
                {"product_specification": state["product_specification"]},
            )
            persist_artifact(state, artifact_type="product_truth_pack", agent="lucien", skill="create-product-truth-pack", content=result)
            return {"product_truth_pack": result, "current_state": "PRODUCT_TRUTH_READY", "error": ""}
        except Exception as exc:
            return failure(state, "truth_pack", exc)

    def messaging(state: ProductLaunchState):
        try:
            result = run(
                "elodie",
                "create-launch-messaging",
                {"product_truth_pack": state["product_truth_pack"]},
            )
            persist_artifact(state, artifact_type="messaging_framework", agent="elodie", skill="create-launch-messaging", content=result)
            return {"messaging_framework": result, "current_state": "MESSAGING_READY", "error": ""}
        except Exception as exc:
            return failure(state, "messaging", exc)

    def commercial(state: ProductLaunchState):
        try:
            result = run(
                "marc",
                "prepare-commercial-launch",
                {
                    "product_specification": state["product_specification"],
                    "product_truth_pack": state["product_truth_pack"],
                },
            )
            persist_artifact(state, artifact_type="commercial_setup", agent="marc", skill="prepare-commercial-launch", content=result)
            return {"commercial_setup": result, "current_state": "COMMERCIAL_READY", "error": ""}
        except Exception as exc:
            return failure(state, "commercial", exc)

    def content(state: ProductLaunchState):
        try:
            result = run(
                "maya",
                "create-launch-content",
                {
                    "messaging_framework": state["messaging_framework"],
                    "product_truth_pack": state["product_truth_pack"],
                },
            )
            persist_artifact(state, artifact_type="content_plan", agent="maya", skill="create-launch-content", content=result)
            return {"content_plan": result, "current_state": "CONTENT_READY", "error": ""}
        except Exception as exc:
            return failure(state, "content", exc)

    def customer(state: ProductLaunchState):
        try:
            result = run(
                "sophie",
                "prepare-customer-readiness",
                {
                    "product_truth_pack": state["product_truth_pack"],
                    "messaging_framework": state["messaging_framework"],
                },
            )
            persist_artifact(state, artifact_type="support_pack", agent="sophie", skill="prepare-customer-readiness", content=result)
            return {"support_pack": result, "current_state": "SUPPORT_READY", "error": ""}
        except Exception as exc:
            return failure(state, "customer", exc)

    def market(state: ProductLaunchState):
        try:
            result = run(
                "nora",
                "check-launch-market-context",
                {"launch_brief": state["launch_brief"]},
            )
            persist_artifact(state, artifact_type="market_context", agent="nora", skill="check-launch-market-context", content=result)
            return {"market_context": result, "current_state": "MARKET_CHECKED", "error": ""}
        except Exception as exc:
            return failure(state, "market", exc)

    def integrate(state: ProductLaunchState):
        try:
            result = run(
                "elena",
                "integrate-launch-readiness",
                {
                    "commercial_setup": state["commercial_setup"],
                    "content_plan": state["content_plan"],
                    "support_pack": state["support_pack"],
                    "market_context": state["market_context"],
                },
            )
            persist_artifact(state, artifact_type="launch_readiness", agent="elena", skill="integrate-launch-readiness", content=result)
            return {"launch_readiness": result, "current_state": "LAUNCH_REVIEW", "error": ""}
        except Exception as exc:
            return failure(state, "integrate", exc)

    def founder_gate(state: ProductLaunchState):
        response = interrupt(
            {
                "type": "founder_gate",
                "gate": "product_launch",
                "workflow_id": state["workflow_id"],
                "allowed_decisions": ["approve", "revise", "hold", "cancel"],
                "launch_readiness": state["launch_readiness"],
            }
        )
        decision = str(response.get("decision") if isinstance(response, dict) else response).lower()
        rationale = response.get("rationale", "") if isinstance(response, dict) else ""
        if decision not in {"approve", "revise", "hold", "cancel"}:
            raise ValueError(f"Invalid founder decision: {decision}")
        if deps.persistence is not None:
            deps.persistence.persist_decision(
                workflow_id=state["workflow_id"],
                decision=decision,
                rationale=rationale,
            )
        return {"founder_decision": decision}

    def route_founder(state: ProductLaunchState):
        return state["founder_decision"]

    def revise(state: ProductLaunchState):
        return {"current_state": "REVISION_REQUIRED", "founder_decision": ""}

    def hold(state: ProductLaunchState):
        return {"current_state": "ON_HOLD"}

    def cancel(state: ProductLaunchState):
        return {"current_state": "CANCELLED"}

    def activate(state: ProductLaunchState):
        try:
            if state.get("activation_executed"):
                return {"current_state": "LIVE"}

            deps.policy.authorize_tool(ToolRequest(agent_id="marc", skill_id="workflow", tool_name="shopify_publish", mode="action"))
            deps.policy.authorize_tool(ToolRequest(agent_id="maya", skill_id="workflow", tool_name="social_publish", mode="action"))
            deps.policy.authorize_tool(ToolRequest(agent_id="sophie", skill_id="workflow", tool_name="community_publish", mode="action"))

            activation_payload = {
                "workflow_id": state["workflow_id"],
                "product_id": state["product_id"],
                "commercial_setup": state["commercial_setup"],
                "content_plan": state["content_plan"],
                "support_pack": state["support_pack"],
            }
            result = deps.execute_activation(activation_payload)

            if deps.persistence is not None:
                deps.persistence.persist_artifact(
                    workflow_id=state["workflow_id"],
                    artifact_type="activation_result",
                    agent_id="marc",
                    skill_id="activate-product-launch",
                    content=result,
                )

            return {
                "activation_result": result,
                "activation_executed": True,
                "activation_key": f"launch:{state['workflow_id']}",
                "current_state": "LIVE",
                "error": "",
            }
        except Exception as exc:
            return failure(state, "activate", exc)

    def learning(state: ProductLaunchState):
        try:
            snapshot = state.get(
                "performance_snapshot",
                {
                    "commerce": {},
                    "content": {},
                    "customer": {},
                    "market": {},
                },
            )
            result = run(
                "elena",
                "capture-launch-learning",
                {"performance_snapshot": snapshot},
            )
            persist_artifact(state, artifact_type="launch_learning", agent="elena", skill="capture-launch-learning", content=result)
            return {"launch_learning": result, "current_state": "COMPLETE", "error": ""}
        except Exception as exc:
            return failure(state, "learning", exc)

    def route_after_stage(state: ProductLaunchState):
        return "error_recovery" if state.get("current_state") == "ERROR" else "next"

    def error_recovery(state: ProductLaunchState):
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

    def route_error_recovery(state: ProductLaunchState):
        if state["recovery_decision"] == "cancel":
            return "error_cancelled"
        return state["failed_stage"]

    def error_cancelled(state: ProductLaunchState):
        return {"current_state": "FAILED", "recoverable": False}

    graph.add_node("validate_spec", validate_spec)
    graph.add_node("launch_brief", launch_brief)
    graph.add_node("truth_pack", truth_pack)
    graph.add_node("messaging", messaging)
    graph.add_node("commercial", commercial)
    graph.add_node("content", content)
    graph.add_node("customer", customer)
    graph.add_node("market", market)
    graph.add_node("integrate", integrate)
    graph.add_node("founder_gate", founder_gate)
    graph.add_node("revise", revise)
    graph.add_node("hold", hold)
    graph.add_node("cancel", cancel)
    graph.add_node("activate", activate)
    graph.add_node("learning", learning)
    graph.add_node("error_recovery", error_recovery)
    graph.add_node("error_cancelled", error_cancelled)

    graph.add_edge(START, "validate_spec")
    graph.add_conditional_edges("validate_spec", route_spec, {"valid": "launch_brief", "invalid": END})

    graph.add_conditional_edges("launch_brief", route_after_stage, {"next": "truth_pack", "error_recovery": "error_recovery"})
    graph.add_conditional_edges("truth_pack", route_after_stage, {"next": "messaging", "error_recovery": "error_recovery"})
    graph.add_conditional_edges("messaging", route_after_stage, {"next": "commercial", "error_recovery": "error_recovery"})
    graph.add_conditional_edges("commercial", route_after_stage, {"next": "content", "error_recovery": "error_recovery"})
    graph.add_conditional_edges("content", route_after_stage, {"next": "customer", "error_recovery": "error_recovery"})
    graph.add_conditional_edges("customer", route_after_stage, {"next": "market", "error_recovery": "error_recovery"})
    graph.add_conditional_edges("market", route_after_stage, {"next": "integrate", "error_recovery": "error_recovery"})
    graph.add_conditional_edges("integrate", route_after_stage, {"next": "founder_gate", "error_recovery": "error_recovery"})

    graph.add_conditional_edges(
        "founder_gate",
        route_founder,
        {"approve": "activate", "revise": "revise", "hold": "hold", "cancel": "cancel"},
    )
    graph.add_edge("revise", "messaging")
    graph.add_edge("hold", END)
    graph.add_edge("cancel", END)

    graph.add_conditional_edges("activate", route_after_stage, {"next": "learning", "error_recovery": "error_recovery"})
    graph.add_conditional_edges("learning", route_after_stage, {"next": END, "error_recovery": "error_recovery"})

    graph.add_conditional_edges(
        "error_recovery",
        route_error_recovery,
        {
            "launch_brief": "launch_brief",
            "truth_pack": "truth_pack",
            "messaging": "messaging",
            "commercial": "commercial",
            "content": "content",
            "customer": "customer",
            "market": "market",
            "integrate": "integrate",
            "activate": "activate",
            "learning": "learning",
            "error_cancelled": "error_cancelled",
        },
    )
    graph.add_edge("error_cancelled", END)

    return graph.compile(checkpointer=MemorySaver())
