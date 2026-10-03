from __future__ import annotations

from typing import Any, Callable, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from amauxboze.registries import AuthorizationService, SkillRegistry

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
    error: str


class ProductLaunchDependencies:
    def __init__(
        self,
        skills: SkillRegistry,
        authorization: AuthorizationService,
        execute_stage: StageExecutor,
        execute_activation: ActivationExecutor,
    ):
        self.skills = skills
        self.authorization = authorization
        self.execute_stage = execute_stage
        self.execute_activation = execute_activation


def build_product_launch_workflow(deps: ProductLaunchDependencies):
    graph = StateGraph(ProductLaunchState)

    def run(agent: str, skill: str, payload: dict[str, Any]) -> dict[str, Any]:
        deps.authorization.authorize_skill(agent, skill)
        deps.skills.validate_input(skill, payload)
        result = deps.execute_stage(agent, skill, payload)
        deps.skills.validate_output(skill, result)
        return result

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
        result = run(
            "elena",
            "define-launch-brief",
            {
                "product_specification": state["product_specification"],
                "launch_objective": state["launch_objective"],
            },
        )
        return {"launch_brief": result, "current_state": "LAUNCH_BRIEF_READY"}

    def truth_pack(state: ProductLaunchState):
        result = run(
            "lucien",
            "create-product-truth-pack",
            {"product_specification": state["product_specification"]},
        )
        return {"product_truth_pack": result, "current_state": "PRODUCT_TRUTH_READY"}

    def messaging(state: ProductLaunchState):
        result = run(
            "elodie",
            "create-launch-messaging",
            {"product_truth_pack": state["product_truth_pack"]},
        )
        return {"messaging_framework": result, "current_state": "MESSAGING_READY"}

    def commercial(state: ProductLaunchState):
        result = run(
            "marc",
            "prepare-commercial-launch",
            {
                "product_specification": state["product_specification"],
                "product_truth_pack": state["product_truth_pack"],
            },
        )
        return {"commercial_setup": result, "current_state": "COMMERCIAL_READY"}

    def content(state: ProductLaunchState):
        result = run(
            "maya",
            "create-launch-content",
            {
                "messaging_framework": state["messaging_framework"],
                "product_truth_pack": state["product_truth_pack"],
            },
        )
        return {"content_plan": result, "current_state": "CONTENT_READY"}

    def customer(state: ProductLaunchState):
        result = run(
            "sophie",
            "prepare-customer-readiness",
            {
                "product_truth_pack": state["product_truth_pack"],
                "messaging_framework": state["messaging_framework"],
            },
        )
        return {"support_pack": result, "current_state": "SUPPORT_READY"}

    def market(state: ProductLaunchState):
        result = run(
            "nora",
            "check-launch-market-context",
            {"launch_brief": state["launch_brief"]},
        )
        return {"market_context": result, "current_state": "MARKET_CHECKED"}

    def integrate(state: ProductLaunchState):
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
        return {"launch_readiness": result, "current_state": "LAUNCH_REVIEW"}

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
        if decision not in {"approve", "revise", "hold", "cancel"}:
            raise ValueError(f"Invalid founder decision: {decision}")
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
        if state.get("activation_executed"):
            return {"current_state": "LIVE"}

        activation_payload = {
            "workflow_id": state["workflow_id"],
            "product_id": state["product_id"],
            "commercial_setup": state["commercial_setup"],
            "content_plan": state["content_plan"],
            "support_pack": state["support_pack"],
        }
        result = deps.execute_activation(activation_payload)
        return {
            "activation_result": result,
            "activation_executed": True,
            "activation_key": f"launch:{state['workflow_id']}",
            "current_state": "LIVE",
        }

    def learning(state: ProductLaunchState):
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
        return {"launch_learning": result, "current_state": "COMPLETE"}

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

    graph.add_edge(START, "validate_spec")
    graph.add_conditional_edges(
        "validate_spec",
        route_spec,
        {"valid": "launch_brief", "invalid": END},
    )
    graph.add_edge("launch_brief", "truth_pack")
    graph.add_edge("truth_pack", "messaging")
    graph.add_edge("messaging", "commercial")
    graph.add_edge("commercial", "content")
    graph.add_edge("content", "customer")
    graph.add_edge("customer", "market")
    graph.add_edge("market", "integrate")
    graph.add_edge("integrate", "founder_gate")

    graph.add_conditional_edges(
        "founder_gate",
        route_founder,
        {
            "approve": "activate",
            "revise": "revise",
            "hold": "hold",
            "cancel": "cancel",
        },
    )
    graph.add_edge("revise", "messaging")
    graph.add_edge("hold", END)
    graph.add_edge("cancel", END)
    graph.add_edge("activate", "learning")
    graph.add_edge("learning", END)

    return graph.compile(checkpointer=MemorySaver())
