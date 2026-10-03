from __future__ import annotations

from typing import Any, Callable, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from amauxboze.contracts import PolicyEngine, ToolRequest
from amauxboze.registries import SkillRegistry
from amauxboze.workflows.content_campaign_persistence import ContentCampaignPersistence

StageExecutor = Callable[[str, str, dict[str, Any]], dict[str, Any]]
PublishExecutor = Callable[[dict[str, Any]], dict[str, Any]]


class ContentCampaignState(TypedDict, total=False):
    workflow_id: str
    campaign_objective: str
    audience: str
    campaign_brief: dict[str, Any]
    message_architecture: dict[str, Any]
    audience_relevance: dict[str, Any]
    evidence_validation: dict[str, Any]
    channel_strategy: dict[str, Any]
    commercial_alignment: dict[str, Any]
    content_package: dict[str, Any]
    brand_review: dict[str, Any]
    founder_decision: str
    publish_result: dict[str, Any]
    performance_snapshot: dict[str, Any]
    campaign_learning: dict[str, Any]
    current_state: str
    published: bool
    publish_key: str
    retry_count: int
    failed_stage: str
    recoverable: bool
    recovery_decision: str
    error: str


class ContentCampaignDependencies:
    def __init__(
        self,
        skills: SkillRegistry,
        policy: PolicyEngine,
        execute_stage: StageExecutor,
        execute_publish: PublishExecutor,
        persistence: ContentCampaignPersistence | None = None,
    ):
        self.skills = skills
        self.policy = policy
        self.execute_stage = execute_stage
        self.execute_publish = execute_publish
        self.persistence = persistence


def build_content_campaign_workflow(deps: ContentCampaignDependencies):
    graph = StateGraph(ContentCampaignState)

    def run(agent: str, skill: str, payload: dict[str, Any]) -> dict[str, Any]:
        deps.policy.authorize_skill(agent, skill)
        deps.skills.validate_input(skill, payload)
        result = deps.execute_stage(agent, skill, payload)
        deps.skills.validate_output(skill, result)
        return result

    def persist(state: ContentCampaignState, artifact_type: str, agent: str, skill: str, content: dict[str, Any]):
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

    def failure(state: ContentCampaignState, stage: str, exc: Exception):
        return {
            "current_state": "ERROR",
            "failed_stage": stage,
            "recoverable": True,
            "error": f"{type(exc).__name__}: {exc}",
            "retry_count": state.get("retry_count", 0),
        }

    def campaign_brief(state: ContentCampaignState):
        try:
            result = run(
                "elena",
                "define-campaign-brief",
                {"campaign_objective": state["campaign_objective"], "audience": state["audience"]},
            )
            persist(state, "campaign_brief", "elena", "define-campaign-brief", result)
            return {"campaign_brief": result, "current_state": "BRIEF_READY", "error": ""}
        except Exception as exc:
            return failure(state, "campaign_brief", exc)

    def message_architecture(state: ContentCampaignState):
        try:
            result = run("elodie", "create-message-architecture", {"campaign_brief": state["campaign_brief"]})
            persist(state, "message_architecture", "elodie", "create-message-architecture", result)
            return {"message_architecture": result, "current_state": "MESSAGE_READY", "error": ""}
        except Exception as exc:
            return failure(state, "message_architecture", exc)

    def audience_relevance(state: ContentCampaignState):
        try:
            result = run(
                "sophie",
                "assess-audience-relevance",
                {"campaign_brief": state["campaign_brief"], "message_architecture": state["message_architecture"]},
            )
            persist(state, "audience_relevance", "sophie", "assess-audience-relevance", result)
            return {"audience_relevance": result, "current_state": "AUDIENCE_CHECKED", "error": ""}
        except Exception as exc:
            return failure(state, "audience_relevance", exc)

    def evidence_validation(state: ContentCampaignState):
        try:
            result = run(
                "nora",
                "validate-campaign-evidence",
                {"message_architecture": state["message_architecture"]},
            )
            persist(state, "evidence_validation", "nora", "validate-campaign-evidence", result)
            return {"evidence_validation": result, "current_state": "EVIDENCE_CHECKED", "error": ""}
        except Exception as exc:
            return failure(state, "evidence_validation", exc)

    def channel_strategy(state: ContentCampaignState):
        try:
            result = run(
                "maya",
                "define-channel-strategy",
                {"campaign_brief": state["campaign_brief"], "message_architecture": state["message_architecture"]},
            )
            persist(state, "channel_strategy", "maya", "define-channel-strategy", result)
            return {"channel_strategy": result, "current_state": "CHANNELS_READY", "error": ""}
        except Exception as exc:
            return failure(state, "channel_strategy", exc)

    def commercial_alignment(state: ContentCampaignState):
        try:
            result = run(
                "marc",
                "align-commercial-objective",
                {"campaign_brief": state["campaign_brief"], "channel_strategy": state["channel_strategy"]},
            )
            persist(state, "commercial_alignment", "marc", "align-commercial-objective", result)
            return {"commercial_alignment": result, "current_state": "COMMERCIAL_ALIGNED", "error": ""}
        except Exception as exc:
            return failure(state, "commercial_alignment", exc)

    def content_production(state: ContentCampaignState):
        try:
            result = run(
                "maya",
                "create-campaign-content",
                {
                    "message_architecture": state["message_architecture"],
                    "channel_strategy": state["channel_strategy"],
                    "commercial_alignment": state["commercial_alignment"],
                    "evidence_validation": state["evidence_validation"],
                },
            )
            persist(state, "content_package", "maya", "create-campaign-content", result)
            return {"content_package": result, "current_state": "CONTENT_READY", "error": ""}
        except Exception as exc:
            return failure(state, "content_production", exc)

    def brand_review(state: ContentCampaignState):
        try:
            result = run(
                "elodie",
                "review-campaign-brand-fit",
                {"content_package": state["content_package"], "message_architecture": state["message_architecture"]},
            )
            persist(state, "brand_review", "elodie", "review-campaign-brand-fit", result)
            return {"brand_review": result, "current_state": "BRAND_REVIEWED", "error": ""}
        except Exception as exc:
            return failure(state, "brand_review", exc)

    def founder_gate(state: ContentCampaignState):
        response = interrupt({
            "type": "founder_gate",
            "gate": "content_campaign",
            "workflow_id": state["workflow_id"],
            "allowed_decisions": ["approve", "revise", "hold", "cancel"],
            "brand_review": state["brand_review"],
        })
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

    def route_founder(state: ContentCampaignState):
        return state["founder_decision"]

    def revise(state: ContentCampaignState):
        return {"current_state": "REVISION_REQUIRED", "founder_decision": ""}

    def hold(state: ContentCampaignState):
        return {"current_state": "ON_HOLD"}

    def cancel(state: ContentCampaignState):
        return {"current_state": "CANCELLED"}

    def publish(state: ContentCampaignState):
        try:
            if state.get("published"):
                return {"current_state": "PUBLISHED"}

            deps.policy.authorize_tool(ToolRequest(agent_id="maya", skill_id="workflow", tool_name="social_publish", mode="action"))
            payload = {
                "workflow_id": state["workflow_id"],
                "content_package": state["content_package"],
                "channel_strategy": state["channel_strategy"],
            }
            result = deps.execute_publish(payload)
            if deps.persistence is not None:
                deps.persistence.persist_artifact(
                    workflow_id=state["workflow_id"],
                    artifact_type="publish_result",
                    agent_id="maya",
                    skill_id="publish-content-campaign",
                    content=result,
                )
            return {
                "publish_result": result,
                "published": True,
                "publish_key": f"campaign:{state['workflow_id']}",
                "current_state": "PUBLISHED",
                "error": "",
            }
        except Exception as exc:
            return failure(state, "publish", exc)

    def learning(state: ContentCampaignState):
        try:
            snapshot = state.get("performance_snapshot", {"content": {}, "commercial": {}, "customer": {}, "market": {}})
            result = run("elena", "capture-campaign-learning", {"performance_snapshot": snapshot})
            persist(state, "campaign_learning", "elena", "capture-campaign-learning", result)
            return {"campaign_learning": result, "current_state": "COMPLETE", "error": ""}
        except Exception as exc:
            return failure(state, "learning", exc)

    def route_after_stage(state: ContentCampaignState):
        return "error_recovery" if state.get("current_state") == "ERROR" else "next"

    def error_recovery(state: ContentCampaignState):
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

    def route_error(state: ContentCampaignState):
        if state["recovery_decision"] == "cancel":
            return "error_cancelled"
        return state["failed_stage"]

    def error_cancelled(state: ContentCampaignState):
        return {"current_state": "FAILED", "recoverable": False}

    for name, fn in [
        ("campaign_brief", campaign_brief),
        ("message_architecture", message_architecture),
        ("audience_relevance", audience_relevance),
        ("evidence_validation", evidence_validation),
        ("channel_strategy", channel_strategy),
        ("commercial_alignment", commercial_alignment),
        ("content_production", content_production),
        ("brand_review", brand_review),
        ("founder_gate", founder_gate),
        ("revise", revise),
        ("hold", hold),
        ("cancel", cancel),
        ("publish", publish),
        ("learning", learning),
        ("error_recovery", error_recovery),
        ("error_cancelled", error_cancelled),
    ]:
        graph.add_node(name, fn)

    graph.add_edge(START, "campaign_brief")
    graph.add_conditional_edges("campaign_brief", route_after_stage, {"next": "message_architecture", "error_recovery": "error_recovery"})
    graph.add_conditional_edges("message_architecture", route_after_stage, {"next": "audience_relevance", "error_recovery": "error_recovery"})
    graph.add_conditional_edges("audience_relevance", route_after_stage, {"next": "evidence_validation", "error_recovery": "error_recovery"})
    graph.add_conditional_edges("evidence_validation", route_after_stage, {"next": "channel_strategy", "error_recovery": "error_recovery"})
    graph.add_conditional_edges("channel_strategy", route_after_stage, {"next": "commercial_alignment", "error_recovery": "error_recovery"})
    graph.add_conditional_edges("commercial_alignment", route_after_stage, {"next": "content_production", "error_recovery": "error_recovery"})
    graph.add_conditional_edges("content_production", route_after_stage, {"next": "brand_review", "error_recovery": "error_recovery"})
    graph.add_conditional_edges("brand_review", route_after_stage, {"next": "founder_gate", "error_recovery": "error_recovery"})

    graph.add_conditional_edges(
        "founder_gate",
        route_founder,
        {"approve": "publish", "revise": "revise", "hold": "hold", "cancel": "cancel"},
    )
    graph.add_edge("revise", "content_production")
    graph.add_edge("hold", END)
    graph.add_edge("cancel", END)

    graph.add_conditional_edges("publish", route_after_stage, {"next": "learning", "error_recovery": "error_recovery"})
    graph.add_conditional_edges("learning", route_after_stage, {"next": END, "error_recovery": "error_recovery"})

    graph.add_conditional_edges(
        "error_recovery",
        route_error,
        {
            "campaign_brief": "campaign_brief",
            "message_architecture": "message_architecture",
            "audience_relevance": "audience_relevance",
            "evidence_validation": "evidence_validation",
            "channel_strategy": "channel_strategy",
            "commercial_alignment": "commercial_alignment",
            "content_production": "content_production",
            "brand_review": "brand_review",
            "publish": "publish",
            "learning": "learning",
            "error_cancelled": "error_cancelled",
        },
    )
    graph.add_edge("error_cancelled", END)

    return graph.compile(checkpointer=MemorySaver())
