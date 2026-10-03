from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from amauxboze.registries import AuthorizationService, SkillRegistry
from amauxboze.workflows.market_intelligence_persistence import MarketIntelligencePersistence

StageExecutor = Callable[[str, str, dict[str, Any]], dict[str, Any]]


class MarketIntelligenceState(TypedDict, total=False):
    workflow_id: str
    watch_topic: str
    geography: str
    research_question: dict[str, Any]
    evidence_pack: dict[str, Any]
    observations: dict[str, Any]
    observations_snapshot: dict[str, Any]
    pattern_analysis: dict[str, Any]
    product_interpretation: dict[str, Any]
    brand_interpretation: dict[str, Any]
    commercial_interpretation: dict[str, Any]
    customer_interpretation: dict[str, Any]
    strategic_insight: dict[str, Any]
    decision_brief: dict[str, Any]
    founder_decision: str
    knowledge_update: dict[str, Any]
    current_state: str
    retry_count: int
    failed_stage: str
    recoverable: bool
    recovery_decision: str
    error: str


class MarketIntelligenceDependencies:
    def __init__(
        self,
        skills: SkillRegistry,
        authorization: AuthorizationService,
        execute_stage: StageExecutor,
        persistence: MarketIntelligencePersistence | None = None,
    ):
        self.skills = skills
        self.authorization = authorization
        self.execute_stage = execute_stage
        self.persistence = persistence


def build_market_intelligence_workflow(deps: MarketIntelligenceDependencies):
    graph = StateGraph(MarketIntelligenceState)

    def run(agent: str, skill: str, payload: dict[str, Any]) -> dict[str, Any]:
        deps.authorization.authorize_skill(agent, skill)
        deps.skills.validate_input(skill, payload)
        result = deps.execute_stage(agent, skill, payload)
        deps.skills.validate_output(skill, result)
        return result

    def persist(state: MarketIntelligenceState, artifact_type: str, agent: str, skill: str, content: dict[str, Any]):
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

    def failure(state: MarketIntelligenceState, stage: str, exc: Exception):
        return {
            "current_state": "ERROR",
            "failed_stage": stage,
            "recoverable": True,
            "error": f"{type(exc).__name__}: {exc}",
            "retry_count": state.get("retry_count", 0),
        }

    def research_question(state: MarketIntelligenceState):
        try:
            result = run(
                "nora",
                "define-research-question",
                {"watch_topic": state["watch_topic"], "geography": state.get("geography", "Global")},
            )
            persist(state, "research_question", "nora", "define-research-question", result)
            return {"research_question": result, "current_state": "QUESTION_DEFINED", "error": ""}
        except Exception as exc:
            return failure(state, "research_question", exc)

    def evidence(state: MarketIntelligenceState):
        try:
            result = run("nora", "collect-market-evidence", {"research_question": state["research_question"]})
            persist(state, "evidence_pack", "nora", "collect-market-evidence", result)
            return {"evidence_pack": result, "current_state": "EVIDENCE_COLLECTED", "error": ""}
        except Exception as exc:
            return failure(state, "evidence", exc)

    def observations(state: MarketIntelligenceState):
        try:
            result = run(
                "nora",
                "capture-market-observations",
                {"evidence_pack": state["evidence_pack"], "geography": state.get("geography", "Global")},
            )
            immutable = deepcopy(result)
            persist(state, "observations", "nora", "capture-market-observations", immutable)
            return {
                "observations": immutable,
                "observations_snapshot": deepcopy(immutable),
                "current_state": "OBSERVATIONS_RECORDED",
                "error": "",
            }
        except Exception as exc:
            return failure(state, "observations", exc)

    def pattern(state: MarketIntelligenceState):
        try:
            result = run("nora", "detect-market-change", {"observations": deepcopy(state["observations"])})
            persist(state, "pattern_analysis", "nora", "detect-market-change", result)
            return {"pattern_analysis": result, "current_state": "PATTERN_ANALYZED", "error": ""}
        except Exception as exc:
            return failure(state, "pattern", exc)

    def interpret_product(state: MarketIntelligenceState):
        try:
            result = run("lucien", "interpret-product-impact", {"pattern_analysis": state["pattern_analysis"], "observations": deepcopy(state["observations"])})
            persist(state, "product_interpretation", "lucien", "interpret-product-impact", result)
            return {"product_interpretation": result, "current_state": "PRODUCT_INTERPRETED", "error": ""}
        except Exception as exc:
            return failure(state, "interpret_product", exc)

    def interpret_brand(state: MarketIntelligenceState):
        try:
            result = run("elodie", "interpret-brand-impact", {"pattern_analysis": state["pattern_analysis"], "observations": deepcopy(state["observations"])})
            persist(state, "brand_interpretation", "elodie", "interpret-brand-impact", result)
            return {"brand_interpretation": result, "current_state": "BRAND_INTERPRETED", "error": ""}
        except Exception as exc:
            return failure(state, "interpret_brand", exc)

    def interpret_commercial(state: MarketIntelligenceState):
        try:
            result = run("marc", "interpret-commercial-impact", {"pattern_analysis": state["pattern_analysis"], "observations": deepcopy(state["observations"])})
            persist(state, "commercial_interpretation", "marc", "interpret-commercial-impact", result)
            return {"commercial_interpretation": result, "current_state": "COMMERCIAL_INTERPRETED", "error": ""}
        except Exception as exc:
            return failure(state, "interpret_commercial", exc)

    def interpret_customer(state: MarketIntelligenceState):
        try:
            result = run("sophie", "interpret-customer-impact", {"pattern_analysis": state["pattern_analysis"], "observations": deepcopy(state["observations"])})
            persist(state, "customer_interpretation", "sophie", "interpret-customer-impact", result)
            return {"customer_interpretation": result, "current_state": "CUSTOMER_INTERPRETED", "error": ""}
        except Exception as exc:
            return failure(state, "interpret_customer", exc)

    def synthesize(state: MarketIntelligenceState):
        try:
            result = run(
                "nora",
                "synthesize-strategic-insight",
                {
                    "pattern_analysis": state["pattern_analysis"],
                    "product_interpretation": state["product_interpretation"],
                    "brand_interpretation": state["brand_interpretation"],
                    "commercial_interpretation": state["commercial_interpretation"],
                    "customer_interpretation": state["customer_interpretation"],
                },
            )
            persist(state, "strategic_insight", "nora", "synthesize-strategic-insight", result)
            return {"strategic_insight": result, "current_state": "INSIGHT_READY", "error": ""}
        except Exception as exc:
            return failure(state, "synthesize", exc)

    def prepare_decision(state: MarketIntelligenceState):
        try:
            result = run("elena", "prepare-strategic-decision", {"strategic_insight": state["strategic_insight"]})
            persist(state, "decision_brief", "elena", "prepare-strategic-decision", result)
            return {"decision_brief": result, "current_state": "DECISION_READY", "error": ""}
        except Exception as exc:
            return failure(state, "prepare_decision", exc)

    def founder_gate(state: MarketIntelligenceState):
        response = interrupt({
            "type": "founder_gate",
            "gate": "strategic_insight",
            "workflow_id": state["workflow_id"],
            "allowed_decisions": ["act", "investigate_further", "monitor", "archive"],
            "decision_brief": state["decision_brief"],
        })
        decision = str(response.get("decision") if isinstance(response, dict) else response).lower()
        rationale = response.get("rationale", "") if isinstance(response, dict) else ""
        if decision not in {"act", "investigate_further", "monitor", "archive"}:
            raise ValueError(f"Invalid founder decision: {decision}")
        if deps.persistence is not None:
            deps.persistence.persist_decision(workflow_id=state["workflow_id"], decision=decision, rationale=rationale)
        return {"founder_decision": decision}

    def knowledge_update(state: MarketIntelligenceState):
        try:
            result = run(
                "nora",
                "update-intelligence-knowledge",
                {
                    "strategic_insight": state["strategic_insight"],
                    "founder_decision": state["founder_decision"],
                    "follow_up_conditions": state["decision_brief"].get("follow_up_conditions", []),
                },
            )
            persist(state, "knowledge_update", "nora", "update-intelligence-knowledge", result)
            return {"knowledge_update": result, "current_state": "KNOWLEDGE_UPDATED", "error": ""}
        except Exception as exc:
            return failure(state, "knowledge_update", exc)

    def route_after_stage(state: MarketIntelligenceState):
        return "error_recovery" if state.get("current_state") == "ERROR" else "next"

    def error_recovery(state: MarketIntelligenceState):
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

    def route_error(state: MarketIntelligenceState):
        if state["recovery_decision"] == "cancel":
            return "error_cancelled"
        return state["failed_stage"]

    def error_cancelled(state: MarketIntelligenceState):
        return {"current_state": "FAILED", "recoverable": False}

    nodes = [
        ("research_question", research_question),
        ("evidence", evidence),
        ("observations", observations),
        ("pattern", pattern),
        ("interpret_product", interpret_product),
        ("interpret_brand", interpret_brand),
        ("interpret_commercial", interpret_commercial),
        ("interpret_customer", interpret_customer),
        ("synthesize", synthesize),
        ("prepare_decision", prepare_decision),
        ("founder_gate", founder_gate),
        ("knowledge_update", knowledge_update),
        ("error_recovery", error_recovery),
        ("error_cancelled", error_cancelled),
    ]
    for name, fn in nodes:
        graph.add_node(name, fn)

    graph.add_edge(START, "research_question")
    sequence = [
        ("research_question", "evidence"),
        ("evidence", "observations"),
        ("observations", "pattern"),
        ("pattern", "interpret_product"),
        ("interpret_product", "interpret_brand"),
        ("interpret_brand", "interpret_commercial"),
        ("interpret_commercial", "interpret_customer"),
        ("interpret_customer", "synthesize"),
        ("synthesize", "prepare_decision"),
        ("prepare_decision", "founder_gate"),
    ]
    for source, target in sequence:
        graph.add_conditional_edges(source, route_after_stage, {"next": target, "error_recovery": "error_recovery"})

    graph.add_edge("founder_gate", "knowledge_update")
    graph.add_conditional_edges("knowledge_update", route_after_stage, {"next": END, "error_recovery": "error_recovery"})

    graph.add_conditional_edges(
        "error_recovery",
        route_error,
        {
            "research_question": "research_question",
            "evidence": "evidence",
            "observations": "observations",
            "pattern": "pattern",
            "interpret_product": "interpret_product",
            "interpret_brand": "interpret_brand",
            "interpret_commercial": "interpret_commercial",
            "interpret_customer": "interpret_customer",
            "synthesize": "synthesize",
            "prepare_decision": "prepare_decision",
            "knowledge_update": "knowledge_update",
            "error_cancelled": "error_cancelled",
        },
    )
    graph.add_edge("error_cancelled", END)

    return graph.compile(checkpointer=MemorySaver())
