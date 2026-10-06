from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from langgraph.types import Command

from amauxboze.adapters import ObsidianAdapter
from amauxboze.models import ModelRouter, RoutingRequest
from amauxboze.registries import AgentRegistry, AuthorizationService, SkillRegistry
from amauxboze.workflows.approvals import ApprovalRequest, request_approval
from amauxboze.workflows.runtime import WorkflowRuntime
from amauxboze.workflows.state import WorkflowState


ModelExecutor = Callable[[str, str], str]


@dataclass
class MinimalWorkflowDependencies:
    agents: AgentRegistry
    skills: SkillRegistry
    authorization: AuthorizationService
    obsidian: ObsidianAdapter
    router: ModelRouter
    execute_model: ModelExecutor


def build_minimal_foundation_workflow(deps: MinimalWorkflowDependencies):
    runtime = WorkflowRuntime()

    def load_context(state: WorkflowState) -> WorkflowState:
        deps.authorization.authorize_skill("elena", "prepare-decision")
        deps.authorization.authorize_tool("elena", "obsidian", mode="read")
        payload = state.get("payload", {})
        context_path = payload.get(
            "context_path", "Organization/00_Operating-Model.md"
        )
        context = deps.obsidian.read_text(context_path)
        return {
            **state,
            "current_state": "CONTEXT_LOADED",
            "agent_id": "elena",
            "skill_id": "prepare-decision",
            "payload": {**payload, "context": context},
        }

    def run_skill(state: WorkflowState) -> WorkflowState:
        payload = state.get("payload", {})
        skill_input = {
            "question": payload["question"],
            "options": payload["options"],
            "evidence": payload.get("evidence", []),
        }
        deps.skills.validate_input("prepare-decision", skill_input)

        provider = deps.router.choose_provider(
            RoutingRequest(
                reasoning="high",
                creativity="low",
                preferred_providers=("lm_studio", "openai", "anthropic"),
            )
        )

        agent = deps.agents.get("elena")
        communication = "\n".join(agent.communication_instructions)
        prompt = (
            f"You are {agent.name}, {agent.role}. {agent.mission} "
            "Prepare a concise founder decision brief.\n\n"
            f"Communication instructions:\n{communication}\n\n"
            f"Company context:\n{payload.get('context', '')}\n\n"
            f"Question: {skill_input['question']}\n"
            f"Options: {skill_input['options']}\n"
            f"Evidence: {skill_input['evidence']}\n"
        )
        answer = deps.execute_model(provider, prompt)

        result = {
            "summary": answer,
            "tradeoffs": [],
            "recommendation_options": skill_input["options"],
        }
        deps.skills.validate_output("prepare-decision", result)

        return {
            **state,
            "current_state": "DECISION_PREPARED",
            "model_provider": provider,
            "result": result,
            "approval_status": "pending",
        }

    def approval_gate(state: WorkflowState) -> WorkflowState:
        decision = request_approval(
            ApprovalRequest(
                workflow_id=state["workflow_id"],
                action="accept_decision_brief",
                reason="Founder approval is required for consequential decisions",
                summary=state.get("result", {}).get("summary", ""),
            )
        )
        mapped = {
            "approve": "approved",
            "reject": "rejected",
            "revise": "revision_required",
        }[decision]
        return {
            **state,
            "current_state": f"APPROVAL_{mapped.upper()}",
            "approval_status": mapped,
        }

    return runtime.build_linear_graph(
        "minimal-foundation",
        [
            ("load_context", load_context),
            ("run_skill", run_skill),
            ("approval_gate", approval_gate),
        ],
    )


def resume_with_decision(graph: Any, config: dict[str, Any], decision: str):
    return graph.invoke(Command(resume=decision), config=config)
