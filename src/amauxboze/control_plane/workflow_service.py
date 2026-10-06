from __future__ import annotations

import json
import os
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import RLock
from uuid import uuid4

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from amauxboze.platform import RegistryPolicyEngine
from amauxboze.platform.context_engine import DefaultContextEngine
from amauxboze.platform.knowledge_provider import ObsidianKnowledgeProvider
from amauxboze.adapters import ObsidianAdapter
from amauxboze.registries import AgentRegistry, AuthorizationService, SkillRegistry
from amauxboze.registries.schema_validation import validate_against_schema
from amauxboze.workflows.model_stage_executor import ModelStageExecutor
from amauxboze.workflows.watch_development import WatchDevelopmentDependencies, build_new_watch_development_workflow
from amauxboze.workflows.product_launch import ProductLaunchDependencies, build_product_launch_workflow
from amauxboze.workflows.content_campaign import ContentCampaignDependencies, build_content_campaign_workflow
from amauxboze.workflows.customer_feedback import CustomerFeedbackDependencies, build_customer_feedback_workflow
from amauxboze.workflows.market_intelligence import MarketIntelligenceDependencies, build_market_intelligence_workflow

from .catalog import PROCESSES
from .contracts import Approval, AppSettings, DecisionCommand, Run, RunCommand, StageAttempt, StartCommand, now
from .model_transport import LiveModelGateway
from .repository import ConflictError, RuntimeRepository
from .simulation import SimulationExecutor


def safe_error(exc: Exception) -> str:
    message = f"{type(exc).__name__}: {exc}"
    for key in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY"):
        secret = os.getenv(key)
        if secret:
            message = message.replace(secret, "[redacted]")
    return message[:1500]


class WorkflowService:
    def __init__(self, root: Path, repository: RuntimeRepository, runtime_path: Path, settings_getter, gateway_factory=LiveModelGateway):
        self.root, self.repo, self.settings_getter = root, repository, settings_getter
        self.agents, self.skills = AgentRegistry(root / "runtime/agents"), SkillRegistry(root / "skills")
        self.agents.load()
        self.skills.load()
        self.policy = RegistryPolicyEngine(AuthorizationService(self.agents, self.skills))
        self.gateway_factory = gateway_factory
        self.checkpoint_connection = sqlite3.connect(runtime_path / "checkpoints.sqlite", check_same_thread=False)
        self.checkpointer = SqliteSaver(self.checkpoint_connection)
        self.checkpointer.setup()
        self.worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix="tom-workflow")
        self.futures = {}
        self.command_lock = RLock()

    def close(self):
        self.worker.shutdown(wait=True)
        self.checkpoint_connection.close()

    def recover(self):
        for raw in self.repo.list("run"):
            if raw["status"] in {"queued", "running"}:
                self.schedule(raw["id"])

    def get(self, run_id) -> Run:
        return Run.model_validate(self.repo.get("run", run_id))

    def start(self, command: StartCommand) -> Run:
        definition = next((p for p in PROCESSES if p.id == command.process_id), None)
        if not definition or definition.version != command.version:
            raise ValueError("Unknown process or outdated version")
        validate_against_schema(command.input, definition.input_schema, label="process input")
        properties = definition.input_schema["properties"]
        if set(command.input) - set(properties):
            raise ValueError("Unknown input field; approval assertions are not accepted")
        for key in definition.input_schema["required"]:
            if not isinstance(command.input[key], str) or not command.input[key].strip():
                raise ValueError(f"Required input is empty: {key}")
        if len(json.dumps(command.input)) > 24000:
            raise ValueError("Process input exceeds context budget")
        if command.mode == "live":
            self.gateway_factory(self.settings_getter())  # Validate routing; errors never switch modes.
        initial = dict(command.input)
        if definition.id == "product-launch":
            approved = self.get(initial.pop("approved_run_id"))
            if approved.process_id != "watch-development" or approved.status != "completed" or approved.state.get("production_decision") != "approve" or approved.mode != command.mode:
                raise ValueError("Product Launch requires a completed, production-approved Watch Development run in the same mode")
            initial.update(product_specification=approved.state["final_specification"], approved_specification=True)
        run_id = str(uuid4())
        run = Run(id=run_id, process_id=definition.id, title=command.input.get("product_working_title", definition.name), mode=command.mode, input=initial)
        identity, created = self.repo.command("start:" + command.idempotency_key, command.model_dump(), [("run", run.model_dump())], run_id)
        if created:
            self.repo.event(identity, "run_created", {"process_id": definition.id, "mode": command.mode})
            self.schedule(identity)
        return self.get(identity)

    def schedule(self, run_id):
        with self.command_lock:
            self.futures[run_id] = self.worker.submit(self._execute, run_id)

    def wait(self, run_id, timeout=180):
        future = self.futures.get(run_id)
        if future:
            future.result(timeout=timeout)
        return self.get(run_id)

    def _graph(self, run: Run):
        cfg = self.settings_getter()
        gateway = self.gateway_factory(cfg) if run.mode == "live" else None
        context_engine = DefaultContextEngine(ObsidianKnowledgeProvider(ObsidianAdapter(cfg.vault_path))) if Path(cfg.vault_path).is_dir() else None
        model_executor = ModelStageExecutor(self.agents, self.skills, gateway, context_engine=context_engine, max_context_chars=cfg.context_chars, workflow_id=run.id) if gateway else SimulationExecutor(self.agents, self.skills)

        def execute_stage(agent, skill, payload):
            current = self.get(run.id)
            last_events = self.repo.events(run_id=run.id)
            reviews = [e["payload"] for e in last_events if e["type"] == "decision_recorded"]
            current.active_agent_ids, current.current_stage, current.updated_at = [agent], skill, now()
            self.repo.save("run", current.model_dump())
            attempts = [a for a in self.repo.list("attempt") if a["run_id"] == run.id and a["skill_id"] == skill]
            attempt = StageAttempt(id=str(uuid4()), run_id=run.id, agent_id=agent, skill_id=skill, status="running", attempt_number=len(attempts) + 1, trace_id=str(uuid4()), provider=cfg.provider if gateway else "simulation", model=cfg.model or None if gateway else None)
            self.repo.save("attempt", attempt.model_dump())
            self.repo.event(run.id, "stage_started", {"agent_id": agent, "skill_id": skill, "attempt_id": attempt.id})
            try:
                if gateway and reviews:
                    model_executor.workflow_feedback = reviews[-1].get("rationale", "")[:4000]
                result = model_executor(agent, skill, payload)
                attempt.status, attempt.artifact = "completed", result
                if gateway and getattr(gateway, "last_response", None):
                    attempt.provider, attempt.model, attempt.usage = gateway.last_response.provider, gateway.last_response.model, gateway.last_response.usage
                else:
                    attempt.provider = "simulation"
                return result
            except Exception as exc:
                attempt.status, attempt.error = "failed", safe_error(exc)
                raise RuntimeError(attempt.error) from None
            finally:
                if gateway and getattr(gateway, "last_response", None):
                    attempt.provider, attempt.model, attempt.usage = gateway.last_response.provider, gateway.last_response.model, gateway.last_response.usage
                attempt.completed_at = now()
                self.repo.save("attempt", attempt.model_dump())
                self.repo.event(run.id, "stage_" + attempt.status, {"agent_id": agent, "skill_id": skill, "attempt_id": attempt.id})

        def external_action(payload):
            if run.mode == "simulation":
                self.repo.event(run.id, "simulated_action", {"notice": "Simulation only; no external action executed"})
                return {"status": "simulated", "external_action_executed": False}
            # No publishing adapter is configured. Never record success.
            raise RuntimeError("Publishing adapter unavailable. Prepared artifacts are retained; no external action was executed.")

        arguments = dict(skills=self.skills, policy=self.policy, execute_stage=execute_stage)
        if run.process_id == "watch-development":
            deps = WatchDevelopmentDependencies(agents=self.agents, **arguments)
            return build_new_watch_development_workflow(deps, checkpointer=self.checkpointer)
        if run.process_id == "product-launch":
            deps = ProductLaunchDependencies(execute_activation=external_action, **arguments)
            return build_product_launch_workflow(deps, checkpointer=self.checkpointer)
        if run.process_id == "content-campaign":
            deps = ContentCampaignDependencies(execute_publish=external_action, **arguments)
            return build_content_campaign_workflow(deps, checkpointer=self.checkpointer)
        if run.process_id == "customer-feedback":
            return build_customer_feedback_workflow(CustomerFeedbackDependencies(**arguments), checkpointer=self.checkpointer)
        return build_market_intelligence_workflow(MarketIntelligenceDependencies(**arguments), checkpointer=self.checkpointer)

    def _execute(self, run_id):
        run = self.get(run_id)
        run.status, run.updated_at = "running", now()
        self.repo.save("run", run.model_dump())
        self.repo.event(run.id, "run_running", {})
        try:
            graph = self._graph(run)
            config = {"configurable": {"thread_id": run.id}, "recursion_limit": 100}
            snapshot = graph.get_state(config)
            invocation = None if snapshot.values else {**run.input, "workflow_id": run.id}
            pending = run.pending_decision
            if pending and snapshot.config and snapshot.config["configurable"].get("checkpoint_id") == pending.get("checkpoint_id"):
                invocation = Command(resume={"decision": pending["decision"], "rationale": pending.get("rationale", "")})
            for update in graph.stream(invocation, config=config, stream_mode="updates"):
                for stage, value in update.items():
                    if stage != "__interrupt__" and isinstance(value, dict):
                        self.repo.event(run.id, "workflow_stage", {"stage": stage, "current_state": value.get("current_state")})
            snapshot = graph.get_state(config)
            current = self.get(run.id)
            current.state, current.pending_decision = dict(snapshot.values), None
            current.revision += 1
            current.updated_at, current.active_agent_ids = now(), []
            interrupts = [i for task in snapshot.tasks for i in task.interrupts]
            if interrupts:
                context = interrupts[0].value
                kind = "recovery" if context.get("type") == "error_recovery" else "approval"
                approval = Approval(id=str(uuid4()), run_id=run.id, revision=current.revision, action=context.get("gate", context.get("failed_stage", "review")), kind=kind, allowed_decisions=context["allowed_decisions"], context=context, checkpoint_id=snapshot.config["configurable"]["checkpoint_id"])
                self.repo.save("approval", approval.model_dump())
                current.approval_id = approval.id
                current.status = "failed" if kind == "recovery" else "waiting_approval"
                current.allowed_commands = approval.allowed_decisions
                current.current_stage = approval.action
            else:
                current.approval_id, current.allowed_commands = None, []
                state = current.state.get("current_state", "")
                current.current_stage = state
                if state == "ON_HOLD":
                    current.status, current.allowed_commands = "held", ["resume", "cancel"]
                elif state == "FAILED" or state == "ERROR":
                    current.status = "failed"
                elif "REJECTED" in state:
                    current.status = "rejected"
                elif "CANCELLED" in state:
                    current.status = "cancelled"
                else:
                    current.status, current.completed_at = "completed", now()
            current.error = current.state.get("error") or None
            self.repo.save("run", current.model_dump())
            self.repo.event(run.id, "run_updated", {"status": current.status, "revision": current.revision})
        except Exception as exc:
            current = self.get(run.id)
            current.status, current.error, current.updated_at = "failed", safe_error(exc), now()
            current.allowed_commands = ["recover", "cancel"]
            current.pending_decision = None
            current.active_agent_ids = []
            current.revision += 1
            self.repo.save("run", current.model_dump())
            self.repo.event(run.id, "run_failed", {"error": current.error})

    def decide(self, approval_id: str, command: DecisionCommand) -> Run:
        with self.command_lock:
            approval = Approval.model_validate(self.repo.get("approval", approval_id))
            run = self.get(approval.run_id)
            if approval.status == "resolved":
                if approval.decision == command.decision and approval.revision == command.revision:
                    return run
                raise ConflictError("Approval already resolved")
            if command.decision not in approval.allowed_decisions:
                raise ValueError("Decision is not allowed by the active workflow gate")
            if run.approval_id != approval.id or run.revision != command.revision:
                raise ConflictError("Approval belongs to an outdated run revision")
            approval.status, approval.decision, approval.rationale = "resolved", command.decision, command.rationale
            run.pending_decision = {"decision": command.decision, "rationale": command.rationale, "checkpoint_id": approval.checkpoint_id}
            run.status, run.approval_id, run.allowed_commands = "queued", None, []
            run.revision += 1
            run.updated_at = now()
            _, applied = self.repo.command("decision:" + command.idempotency_key, {"approval_id": approval_id, **command.model_dump()}, [("approval", approval.model_dump()), ("run", run.model_dump())], run.id, [("run", run.id, command.revision)])
            if applied:
                self.repo.event(run.id, "decision_recorded", {"approval_id": approval.id, "decision": command.decision, "rationale": command.rationale})
                self.schedule(run.id)
            return self.get(run.id)

    def command(self, run_id: str, action: str, command: RunCommand) -> Run:
        with self.command_lock:
            run = self.get(run_id)
            if action not in run.allowed_commands:
                raise ConflictError("Command is not allowed in this run state")
            if run.revision != command.revision:
                raise ConflictError("Run revision changed")
            if action == "cancel":
                run.status, run.allowed_commands, run.updated_at = "cancelled", [], now()
            else:
                if action == "resume":
                    graph = self._graph(run)
                    predecessor = {"watch-development": "integrate", "product-launch": "integrate", "content-campaign": "brand_review"}[run.process_id]
                    graph.update_state({"configurable": {"thread_id": run.id}}, {"current_state": "REOPENED", "founder_decision": ""}, as_node=predecessor)
                run.status, run.allowed_commands = "queued", []
            run.revision += 1
            _, applied = self.repo.command("run-command:" + command.idempotency_key, {"run_id": run_id, "action": action, **command.model_dump()}, [("run", run.model_dump())], run.id, [("run", run.id, command.revision)])
            if applied and action != "cancel":
                self.schedule(run.id)
            self.repo.event(run.id, "run_command", {"action": action})
            return self.get(run.id)
