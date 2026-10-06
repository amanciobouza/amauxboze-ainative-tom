from __future__ import annotations

from datetime import datetime, timedelta, timezone
from statistics import median

from pydantic import Field

from .contracts import DTO, now


class AgentActivity(DTO):
    agent_id: str
    state: str
    active_assignments: list[dict] = Field(default_factory=list)
    waiting_assignments: list[dict] = Field(default_factory=list)
    observed_at: str = Field(default_factory=now)
    freshness: str = "current"


class KPI(DTO):
    id: str
    name: str
    value: float | int | None
    unit: str
    formula: str
    source: str = "Persistierte Prozessläufe"
    observed_at: str = Field(default_factory=now)
    coverage: str
    unavailable_reason: str | None = None
    filter_status: str | None = None


class Dashboard(DTO):
    mode: str
    period_start: str
    period_end: str
    kpis: list[KPI]
    recent_runs: list[dict]
    pending_approvals: list[dict]
    blocked_runs: list[dict]
    learnings: list[dict]


def agent_activity(workflows, agent_id) -> AgentActivity:
    runs = {r["id"]: r for r in workflows.repo.list("run")}
    active, waiting = [], []
    for run in runs.values():
        if agent_id in run["active_agent_ids"] and run["status"] == "running":
            active.append({"run_id": run["id"], "title": run["title"], "stage": run["current_stage"], "mode": run["mode"]})
        if run["status"] in {"waiting_approval", "failed", "held"}:
            attempts = [a for a in workflows.repo.list("attempt") if a["run_id"] == run["id"]]
            last = sorted(attempts, key=lambda a: a["started_at"], reverse=True)
            if last and last[0]["agent_id"] == agent_id:
                waiting.append({"run_id": run["id"], "title": run["title"], "stage": run["current_stage"], "status": run["status"], "mode": run["mode"]})
    state = "working" if active else ("blocked" if any(a["status"] == "failed" for a in waiting) else "waiting_approval" if waiting else "idle")
    return AgentActivity(agent_id=agent_id, state=state, active_assignments=active, waiting_assignments=waiting)


def dashboard(repo, mode="live", days=7, timestamp=None) -> Dashboard:
    end = timestamp or datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    all_runs = [r for r in repo.list("run") if r["mode"] == mode]
    terminal = [r for r in all_runs if r["status"] in {"completed", "failed", "rejected", "cancelled"} and start <= datetime.fromisoformat(r.get("completed_at") or r["updated_at"]) < end]
    completed = [r for r in terminal if r["status"] == "completed"]
    active = [r for r in all_runs if r["status"] in {"queued", "running", "waiting_approval", "held"}]
    pending = [a for a in repo.list("approval") if a["status"] == "pending" and any(r["id"] == a["run_id"] for r in all_runs)]
    failed = [r for r in all_runs if r["status"] == "failed"]
    durations = [(datetime.fromisoformat(r["completed_at"]) - datetime.fromisoformat(r["created_at"])).total_seconds() / 60 for r in completed]
    coverage = f"{len(all_runs)} eindeutige Läufe · {days} Tage · {mode}"
    learnings = [{"run_id": r["id"], "title": r["title"], "type": key, "content": r["state"][key]} for r in completed for key in ("learning_record", "campaign_learning", "launch_learning", "knowledge_update") if key in r["state"]]
    return Dashboard(mode=mode, period_start=start.isoformat(), period_end=end.isoformat(),
        kpis=[
            KPI(id="active", name="Aktive Prozesse", value=len(active), unit="Läufe", formula="queued + running + waiting_approval + held, zum Snapshot", coverage=coverage, filter_status="active"),
            KPI(id="approvals", name="Offene Entscheidungen", value=len(pending), unit="Freigaben", formula="Offene Approval-Envelopes; inklusive Fehler-Recovery", coverage=coverage),
            KPI(id="completed", name="Abgeschlossen", value=len(completed), unit="Läufe", formula="Abgeschlossene Läufe in [Periodenstart, Periodenende)", coverage=coverage, filter_status="completed"),
            KPI(id="success", name="Abschlussquote", value=round(100 * len(completed) / len(terminal), 1) if terminal else None, unit="%", formula=f"completed / (completed + failed + rejected + cancelled); Nenner: {len(terminal)}", coverage=coverage, unavailable_reason=None if terminal else "Keine terminalen Läufe im Zeitfenster"),
            KPI(id="duration", name="Mediane Durchlaufzeit", value=round(median(durations), 1) if durations else None, unit="Min.", formula="Median(completed_at − created_at), inklusive Wartezeit", coverage=coverage, unavailable_reason=None if durations else "Noch keine abgeschlossenen Läufe"),
            KPI(id="learnings", name="Neue Learnings", value=len(learnings), unit="Referenzen", formula="Eindeutige Learning-Artefakte abgeschlossener Läufe im Zeitfenster; Vault-Export separat", coverage=coverage),
            KPI(id="revenue", name="Umsatz", value=None, unit="CHF", formula="Summe Netto-Umsatz im Zeitfenster", source="Commerce MetricsProvider", coverage="Keine Datenquelle", unavailable_reason="Kein Commerce-Connector verbunden"),
            KPI(id="orders", name="Bestellungen", value=None, unit="Orders", formula="Eindeutige bezahlte Bestellungen im Zeitfenster", source="Commerce MetricsProvider", coverage="Keine Datenquelle", unavailable_reason="Kein Commerce-Connector verbunden"),
        ], recent_runs=all_runs[:6], pending_approvals=pending, blocked_runs=failed, learnings=learnings[:10])
