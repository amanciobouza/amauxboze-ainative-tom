from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from threading import RLock
from uuid import uuid4

from amauxboze.workflows.model_stage_executor import ModelStageExecutor
from .contracts import Contribution, DecisionCommand, Experiment, ExperimentResult, Improvement, Retrospective, RetrospectiveStart, now
from .repository import ConflictError
from .workflow_service import safe_error


class RetrospectiveService:
    def __init__(self, workflows):
        self.workflows, self.repo = workflows, workflows.repo
        self.worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix="tom-retrospective")
        self.futures = {}
        self.lock = RLock()

    def close(self):
        self.worker.shutdown(wait=True)

    def get(self, identity):
        return Retrospective.model_validate(self.repo.get("retrospective", identity))

    def start(self, command: RetrospectiveStart):
        runs = [self.workflows.get(identity) for identity in dict.fromkeys(command.run_ids)]
        if any(run.status != "completed" for run in runs) or len({r.mode for r in runs}) != 1:
            raise ValueError("Retrospectives require completed runs in one execution mode")
        if len(set(command.participant_ids)) != len(command.participant_ids):
            raise ValueError("Duplicate participants")
        for agent in command.participant_ids:
            self.workflows.policy.authorize_skill(agent, "retrospective-contribute")
        identity = str(uuid4())
        retro = Retrospective(id=identity, title=command.title, run_ids=[r.id for r in runs], participant_ids=command.participant_ids, mode=runs[0].mode)
        result, created = self.repo.command("retro-start:" + command.idempotency_key, command.model_dump(), [("retrospective", retro.model_dump())], identity)
        if created:
            self.schedule(result)
        return self.get(result)

    def schedule(self, identity):
        self.futures[identity] = self.worker.submit(self._collect, identity)

    def wait(self, identity):
        self.futures[identity].result(timeout=600)
        return self.get(identity)

    def recover(self):
        for item in self.repo.list("retrospective"):
            if item["status"] in {"draft", "collecting", "synthesizing"}:
                retro = self.get(item["id"])
                retro.status, retro.error = "failed", "Application restarted during collection. Retry resumes retained contributions."
                self.repo.save("retrospective", retro.model_dump())

    def _save(self, retro):
        retro.updated_at = now()
        self.repo.save("retrospective", retro.model_dump())
        self.repo.event(retro.id, "retrospective_updated", {"status": retro.status, "revision": retro.revision})

    def _collect(self, identity):
        retro = self.get(identity)
        try:
            runs = [self.workflows.get(r) for r in retro.run_ids]
            budget = min(12000, self.workflows.settings_getter().context_chars)
            evidence = json.dumps([{"run_id": r.id, "process_id": r.process_id, "status": r.status, "state": r.state} for r in runs], ensure_ascii=False)[:budget]
            retro.status, retro.error = "collecting", None
            self._save(retro)
            executor = None
            if retro.mode == "live":
                gateway = self.workflows.gateway_factory(self.workflows.settings_getter())
                executor = ModelStageExecutor(self.workflows.agents, self.workflows.skills, gateway)
            for agent in retro.participant_ids:
                if any(c.author_id == agent for c in retro.contributions):
                    continue
                if executor:
                    result = executor(agent, "retrospective-contribute", {"evidence": evidence, "run_refs": retro.run_ids})
                    contribution = Contribution(author_id=agent, **result)
                    if not set(contribution.evidence_refs) <= set(retro.run_ids):
                        raise ValueError("Contribution cites evidence outside selected runs")
                else:
                    contribution = Contribution(author_id=agent, evidence_refs=retro.run_ids, observation=f"SIMULATION · {len(runs)} abgeschlossene Demonstrationsläufe als Kontext.", interpretation="Der Ablauf ist demonstriert. Geschäftliche Wirksamkeit ist nicht belegt.", proposal="Bei einem echten Lauf zuerst ein messbares Ziel definieren.", evidence_gap="Keine realen Marktergebnisse oder Kundenmetriken vorhanden.")
                retro.contributions.append(contribution)
                self._save(retro)
            retro.status = "synthesizing"
            self._save(retro)
            if executor:
                result = executor("elena", "retrospective-synthesize", {"contributions": [c.model_dump() for c in retro.contributions], "run_refs": retro.run_ids})
                retro.improvements = [Improvement.model_validate(i) for i in result["improvements"]][:3]
            else:
                retro.improvements = [Improvement(owner_id="elena", hypothesis="SIMULATION · Ein explizites Erfolgskriterium reduziert unklare Entscheidungen.", baseline="Noch keine Live-Baseline; vor dem Experiment anhand von 3 realen Läufen erfassen.", metric="Anteil der Briefs mit messbarem Erfolgskriterium", target="100 % der nächsten 3 Briefs", risk="Nur Entwurfsvergleich, keine produktive Änderung.")]
            for improvement in retro.improvements:
                self.workflows.agents.get(improvement.owner_id)
            retro.status = "awaiting_review"
            retro.revision += 1
            self._save(retro)
        except Exception as exc:
            retro.status, retro.error = "failed", safe_error(exc)
            retro.revision += 1
            self._save(retro)

    def review(self, identity, command: DecisionCommand):
        with self.lock:
            retro = self.get(identity)
            allowed = {"awaiting_review": {"approve", "reject", "hold"}, "held": {"resume", "reject"}, "failed": {"retry", "reject"}}
            if command.decision not in allowed.get(retro.status, set()):
                raise ConflictError("Review decision is not allowed in this state")
            if command.revision != retro.revision:
                raise ConflictError("Retrospective revision changed")
            if command.decision == "approve":
                retro.status = "approved"
                retro.experiments = [Experiment(id=str(uuid4()), improvement=i) for i in retro.improvements]
            elif command.decision == "reject":
                retro.status = "rejected"
            elif command.decision == "hold":
                retro.status = "held"
            elif command.decision == "resume":
                retro.status = "awaiting_review"
            else:
                retro.status = "draft"
            old_revision = retro.revision
            retro.revision += 1
            retro.updated_at = now()
            _, applied = self.repo.command("retro-review:" + command.idempotency_key, {"id": identity, **command.model_dump()}, [("retrospective", retro.model_dump())], identity, [("retrospective", identity, old_revision)])
            if applied:
                self.repo.event(identity, "retrospective_review", {"decision": command.decision, "rationale": command.rationale})
                if command.decision == "retry":
                    self.schedule(identity)
            return self.get(identity)

    def experiment_start(self, identity, experiment_id, command):
        with self.lock:
            retro = self.get(identity)
            if retro.status not in {"approved", "experimenting", "evaluating"} or retro.revision != command.revision:
                raise ConflictError("Experiment start needs approved current review")
            experiment = next((e for e in retro.experiments if e.id == experiment_id), None)
            if not experiment or experiment.status != "proposed":
                raise ConflictError("Experiment is not proposed")
            # Approval permits manually recorded sandbox experiments, never production mutations.
            experiment.status, retro.status = "experimenting", "experimenting"
            old = retro.revision
            retro.revision += 1
            self.repo.command("experiment-start:" + command.idempotency_key, {"retro": identity, "experiment": experiment_id, **command.model_dump()}, [("retrospective", retro.model_dump())], identity, [("retrospective", identity, old)])
            self.repo.event(identity, "experiment_started", {"experiment_id": experiment_id})
            return self.get(identity)

    def evaluate(self, identity, experiment_id, command: ExperimentResult):
        with self.lock:
            retro = self.get(identity)
            if retro.revision != command.revision:
                raise ConflictError("Retrospective revision changed")
            experiment = next((e for e in retro.experiments if e.id == experiment_id), None)
            if not experiment or experiment.status != "experimenting":
                raise ConflictError("Experiment must be explicitly started before evaluation")
            experiment.status, experiment.evidence, experiment.outcome, experiment.rationale = "closed", command.evidence, command.outcome, command.rationale
            retro.status = "closed" if all(e.status == "closed" for e in retro.experiments) else "evaluating"
            old = retro.revision
            retro.revision += 1
            self.repo.command("experiment-result:" + command.idempotency_key, {"retro": identity, "experiment": experiment_id, **command.model_dump()}, [("retrospective", retro.model_dump())], identity, [("retrospective", identity, old)])
            self.repo.event(identity, "experiment_evaluated", {"experiment_id": experiment_id, "outcome": command.outcome})
            return self.get(identity)
