import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from amauxboze.control_plane.app import ROOT, create_app
from amauxboze.control_plane.catalog import validate_organization
from amauxboze.control_plane.contracts import AppSettings, Organization, OrganizationNode, Run
from amauxboze.control_plane.model_transport import LiveModelGateway, validate_settings
from amauxboze.control_plane.read_models import dashboard
from amauxboze.control_plane.repository import ConflictError, SQLiteRepository


@pytest.fixture
def application(tmp_path):
    app = create_app(runtime_path=tmp_path / "runtime")
    with TestClient(app) as client:
        yield app, client


def start(app, client, process="watch-development", inputs=None, mode="simulation", key=None):
    values = inputs or {"founder_brief": "Eine Uhr mit klarem Erfolgskriterium", "product_working_title": "Purpose One", "constraints": ["CHF 350"]}
    response = client.post("/api/runs", json={"process_id": process, "mode": mode, "input": values, "idempotency_key": key or str(uuid4())})
    assert response.status_code == 202, response.text
    return app.state.workflows.wait(response.json()["id"])


def decide(app, client, run, decision="approve", key=None):
    approval = client.get(f"/api/runs/{run.id}").json()["approval"]
    assert approval
    response = client.post(f"/api/approvals/{approval['id']}/decision", json={"decision": decision, "revision": run.revision, "rationale": "Reviewed in test", "idempotency_key": key or str(uuid4())})
    assert response.status_code == 200, response.text
    return app.state.workflows.wait(run.id)


def completed_watch(app, client):
    run = start(app, client)
    assert run.status == "waiting_approval"
    run = decide(app, client, run)
    assert run.status == "waiting_approval"
    return decide(app, client, run)


def test_resources_are_real_and_typed(application):
    app, client = application
    assert client.get("/api/health").json()["status"] == "ok"
    org = client.get("/api/organization").json()
    assert len(org["nodes"]) == 9
    assert org["nodes"][0]["kind"] == "human"
    assert len(org["departments"]) == 7
    assert len(client.get("/api/processes").json()) == 5
    elena = client.get("/api/agents/elena").json()
    assert elena["communication_instructions"] and elena["biography_source"] == "agents/elena.md"
    assert elena["activity"]["state"] == "idle"
    assert client.get("/api/agents/missing").status_code == 404
    assert client.get("/api/skills/prepare-decision").json()["version"]
    assert client.post("/api/runs", json={}).status_code == 422
    assert client.post("/api/runs", headers={"Origin": "https://evil.example"}, json={}).status_code == 403
    assert client.get("/api/health", headers={"Host": "evil.example"}).status_code == 400


def test_watch_restart_preserves_every_approval_and_history(tmp_path):
    app = create_app(runtime_path=tmp_path)
    with TestClient(app) as client:
        run = start(app, client)
        run_id = run.id
        attempt_ids = {a["id"] for a in client.get(f"/api/runs/{run_id}").json()["attempts"]}
    app = create_app(runtime_path=tmp_path)
    with TestClient(app) as client:
        run = app.state.workflows.get(run_id)
        run = decide(app, client, run)
        assert run.status == "waiting_approval"
        assert run.current_stage == "production_approval"
    app = create_app(runtime_path=tmp_path)
    with TestClient(app) as client:
        run = decide(app, client, app.state.workflows.get(run_id))
        assert run.status == "completed"
        attempts = client.get(f"/api/runs/{run_id}").json()["attempts"]
        assert attempt_ids <= {a["id"] for a in attempts}
        assert all(a["attempt_number"] == 1 for a in attempts)
        assert run.state["production_decision"] == "approve"


@pytest.mark.parametrize("process,inputs,decision", [
    ("content-campaign", {"campaign_objective": "Positionierung schärfen", "audience": "Uhreninteressierte"}, "approve"),
    ("customer-feedback", {"source": "review", "raw_feedback": "Krone zu klein", "customer_context": {}}, "approve"),
    ("market-intelligence", {"watch_topic": "Microbrands", "geography": "Schweiz"}, "monitor"),
])
def test_other_business_processes_execute_and_resume(application, process, inputs, decision):
    app, client = application
    run = start(app, client, process, inputs)
    assert run.status == "waiting_approval", run.error
    run = decide(app, client, run, decision)
    assert run.status == "completed", run.error
    assert all(a["provider"] == "simulation" for a in client.get(f"/api/runs/{run.id}").json()["attempts"])


def test_product_launch_provenance_and_simulated_activation(application):
    app, client = application
    watch = completed_watch(app, client)
    values = {"approved_run_id": watch.id, "product_id": "purpose-one", "launch_objective": "Launch vorbereiten"}
    run = start(app, client, "product-launch", values)
    assert run.status == "waiting_approval", run.error
    run = decide(app, client, run)
    assert run.status == "completed", run.error
    assert run.state["activation_result"]["external_action_executed"] is False
    response = client.post("/api/runs", json={"process_id": "product-launch", "mode": "live", "input": values, "idempotency_key": str(uuid4())})
    assert response.status_code == 422
    values["approved_specification"] = True
    assert client.post("/api/runs", json={"process_id": "product-launch", "mode": "simulation", "input": values, "idempotency_key": str(uuid4())}).status_code == 422


def test_start_idempotency_and_stale_decisions(application):
    app, client = application
    key = str(uuid4())
    run = start(app, client, key=key)
    again = start(app, client, key=key)
    assert again.id == run.id
    assert len(app.state.repository.list("run")) == 1
    approval = client.get(f"/api/runs/{run.id}").json()["approval"]
    payload = {"decision": "approve", "revision": run.revision - 1, "idempotency_key": str(uuid4())}
    assert client.post(f"/api/approvals/{approval['id']}/decision", json=payload).status_code == 409
    payload["revision"], payload["decision"] = run.revision, "publish_everything"
    assert client.post(f"/api/approvals/{approval['id']}/decision", json=payload).status_code == 422
    payload["decision"] = "approve"
    response = client.post(f"/api/approvals/{approval['id']}/decision", json=payload)
    assert response.status_code == 200
    app.state.workflows.wait(run.id)
    assert client.post(f"/api/approvals/{approval['id']}/decision", json=payload).status_code == 200
    payload["decision"] = "reject"
    assert client.post(f"/api/approvals/{approval['id']}/decision", json=payload).status_code == 409
    assert all(a["attempt_number"] == 1 for a in app.state.repository.list("attempt"))


def test_hold_reopens_gate_without_approval(application):
    app, client = application
    run = decide(app, client, start(app, client), "hold")
    assert run.status == "held"
    response = client.post(f"/api/runs/{run.id}/resume", json={"revision": run.revision, "idempotency_key": str(uuid4())})
    assert response.status_code == 200, response.text
    run = app.state.workflows.wait(run.id)
    assert run.status == "waiting_approval"
    assert run.current_stage == "approve_for_spec"
    assert "final_specification" not in run.state


def test_model_failure_is_recoverable_and_never_simulated(tmp_path):
    class UnavailableGateway:
        def __init__(self, settings): pass
        def invoke(self, request): raise RuntimeError("Model offline")
    app = create_app(runtime_path=tmp_path, gateway_factory=UnavailableGateway)
    with TestClient(app) as client:
        run = start(app, client, mode="live")
        assert run.status == "failed"
        assert "Model offline" in run.error
        approval = client.get(f"/api/runs/{run.id}").json()["approval"]
        assert approval["kind"] == "recovery"
        assert approval["allowed_decisions"] == ["retry", "cancel"]
        run = decide(app, client, run, "retry")
        assert run.status == "failed"
        assert not any(a["provider"] == "simulation" for a in app.state.repository.list("attempt"))


def test_settings_local_only_and_model_gateway_guard(application):
    _, client = application
    cfg = client.get("/api/settings").json()
    cfg.update(provider="openai", privacy="local_only")
    assert client.put("/api/settings", json=cfg).status_code == 422
    cfg.update(provider="lm_studio", lm_studio_url="https://evil.example")
    assert client.put("/api/settings", json=cfg).status_code == 422
    cfg.update(lm_studio_url="http://127.0.0.1:1234")
    assert client.put("/api/settings", json=cfg).status_code == 200
    with pytest.raises(ValueError):
        LiveModelGateway(AppSettings(vault_path="x", provider="anthropic", privacy="local_only"))


def test_knowledge_search_and_traversal(application, tmp_path):
    _, client = application
    vault = tmp_path / "vault"
    (vault / "Learnings").mkdir(parents=True)
    (vault / "Learnings" / "Insight.md").write_text("# Evidence\nTest insight", encoding="utf-8")
    (tmp_path / "outside.md").write_text("Private", encoding="utf-8")
    cfg = client.get("/api/settings").json()
    cfg["vault_path"] = str(vault)
    client.put("/api/settings", json=cfg)
    assert len(client.get("/api/knowledge?q=insight").json()["items"]) == 1
    assert client.get("/api/knowledge/note?path=Learnings/Insight.md").json()["content"].startswith("# Evidence")
    assert client.get("/api/knowledge/note?path=../outside.md").status_code == 403
    assert client.get("/api/knowledge?scope=..").status_code == 403
    assert client.get("/api/knowledge/note?path=secret.env").status_code == 403


def test_retrospective_review_experiment_and_no_simulation_export(application):
    app, client = application
    run = completed_watch(app, client)
    payload = {"title": "Was lernen wir?", "run_ids": [run.id], "participant_ids": ["elena", "nora"], "idempotency_key": str(uuid4())}
    response = client.post("/api/retrospectives", json=payload)
    assert response.status_code == 202, response.text
    identity = response.json()["id"]
    retro = app.state.retrospectives.wait(identity)
    assert retro.status == "awaiting_review"
    assert len(retro.contributions) == 2 and retro.contributions[0].evidence_gap
    assert client.post("/api/retrospectives", json=payload).json()["id"] == identity
    response = client.post(f"/api/retrospectives/{identity}/review", json={"decision": "approve", "revision": retro.revision, "idempotency_key": str(uuid4())})
    assert response.status_code == 200
    retro = response.json()
    experiment = retro["experiments"][0]
    result_path = f"/api/retrospectives/{identity}/experiments/{experiment['id']}/result"
    result = {"revision": retro["revision"], "outcome": "inconclusive", "evidence": "Only demonstration data", "rationale": "No live baseline available", "idempotency_key": str(uuid4())}
    assert client.post(result_path, json=result).status_code == 409
    response = client.post(f"/api/retrospectives/{identity}/experiments/{experiment['id']}/start", json={"revision": retro["revision"], "idempotency_key": str(uuid4())})
    assert response.status_code == 200
    result["revision"] = response.json()["revision"]
    response = client.post(result_path, json=result)
    assert response.status_code == 200
    assert response.json()["status"] == "closed"
    assert response.json()["experiments"][0]["outcome"] == "inconclusive"
    assert client.post(f"/api/retrospectives/{identity}/export", json={"revision": response.json()["revision"], "idempotency_key": str(uuid4())}).status_code == 422


def test_kpi_window_missing_sources_and_duplicate_events(tmp_path):
    repo = SQLiteRepository(tmp_path / "runtime.sqlite")
    timestamp = datetime.now(timezone.utc)
    for identity, delta in [("inside", timedelta(days=1)), ("at_end", timedelta()), ("at_start", timedelta(days=7))]:
        finished = timestamp - delta
        run = Run(id=identity, process_id="watch-development", title=identity, mode="live", status="completed", input={}, created_at=(finished - timedelta(minutes=10)).isoformat(), updated_at=finished.isoformat(), completed_at=finished.isoformat())
        repo.save("run", run.model_dump())
        repo.event(identity, "run_updated", {})
        repo.event(identity, "run_updated", {})
    metrics = {k.id: k for k in dashboard(repo, timestamp=timestamp).kpis}
    assert metrics["completed"].value == 2
    assert metrics["duration"].value == 10
    assert metrics["revenue"].value is None
    assert metrics["success"].value == 100
    assert dashboard(repo, mode="simulation", timestamp=timestamp).kpis[3].value is None
    events = repo.events()
    assert repo.events(after=events[2]["id"]) == events[3:]
    repo.close()


def test_organization_rejects_duplicates_cycles_and_missing_refs():
    base = OrganizationNode(id="a", kind="agent", display_name="A", role="A", mission="A", parent_id="a")
    with pytest.raises(ValueError): validate_organization(Organization(nodes=[base], departments=[]))
    base.parent_id = "missing"
    with pytest.raises(ValueError): validate_organization(Organization(nodes=[base], departments=[]))
    base.parent_id = None
    with pytest.raises(ValueError): validate_organization(Organization(nodes=[base, base], departments=[]))


@pytest.mark.parametrize("process,inputs,decision", [
    ("content-campaign", {"campaign_objective": "Clarity", "audience": "Watch collectors"}, "approve"),
    ("customer-feedback", {"source": "review", "raw_feedback": "Small crown"}, "approve"),
    ("market-intelligence", {"watch_topic": "Microbrands"}, "archive"),
])
def test_restart_at_other_business_gates(tmp_path, process, inputs, decision):
    app = create_app(runtime_path=tmp_path)
    with TestClient(app) as client:
        run = start(app, client, process, inputs)
        assert run.status == "waiting_approval"
        before = [a["id"] for a in app.state.repository.list("attempt")]
    app = create_app(runtime_path=tmp_path)
    with TestClient(app) as client:
        run = decide(app, client, app.state.workflows.get(run.id), decision)
        assert run.status == "completed", run.error
        attempts = app.state.repository.list("attempt")
        assert set(before) <= {a["id"] for a in attempts}
        assert all(a["attempt_number"] == 1 for a in attempts)


def test_launch_restart_and_held_campaign_resume(tmp_path):
    app = create_app(runtime_path=tmp_path)
    with TestClient(app) as client:
        watch = completed_watch(app, client)
        launch = start(app, client, "product-launch", {"approved_run_id": watch.id, "product_id": "test", "launch_objective": "Prepare launch"})
        campaign = start(app, client, "content-campaign", {"campaign_objective": "Clarity", "audience": "Collectors"})
        campaign = decide(app, client, campaign, "hold")
    app = create_app(runtime_path=tmp_path)
    with TestClient(app) as client:
        launch = decide(app, client, app.state.workflows.get(launch.id))
        assert launch.status == "completed"
        campaign = app.state.workflows.get(campaign.id)
        client.post(f"/api/runs/{campaign.id}/resume", json={"revision": campaign.revision, "idempotency_key": str(uuid4())})
        campaign = app.state.workflows.wait(campaign.id)
        assert campaign.status == "waiting_approval"
        assert not campaign.state.get("published")


def test_live_publication_stops_at_missing_adapter(tmp_path):
    from amauxboze.contracts import ModelResponse
    from amauxboze.control_plane.simulation import example
    class ContractGateway:
        def __init__(self, settings): pass
        def invoke(self, request):
            return ModelResponse(provider="test-live-transport", content=json.dumps(example(request.output_schema)))
    app = create_app(runtime_path=tmp_path, gateway_factory=ContractGateway)
    with TestClient(app) as client:
        run = start(app, client, "content-campaign", {"campaign_objective": "Clarity", "audience": "Collectors"}, mode="live")
        assert run.status == "waiting_approval"
        run = decide(app, client, run)
        assert run.status == "failed"
        assert "Publishing adapter unavailable" in run.error
        assert not run.state.get("published")
        assert not any(e["type"] == "simulated_action" for e in app.state.repository.events(run_id=run.id))


def test_reviewed_live_learning_export_is_audited_and_replay_safe(application, tmp_path):
    from amauxboze.control_plane.contracts import Retrospective
    app, client = application
    vault = tmp_path / "vault"
    vault.mkdir()
    cfg = client.get("/api/settings").json()
    cfg["vault_path"] = str(vault)
    client.put("/api/settings", json=cfg)
    retro = Retrospective(id=str(uuid4()), title="Reviewed learning", run_ids=[], participant_ids=["elena"], mode="live", status="closed")
    app.state.repository.save("retrospective", retro.model_dump())
    command = {"revision": retro.revision, "idempotency_key": str(uuid4())}
    response = client.post(f"/api/retrospectives/{retro.id}/export", json=command)
    assert response.status_code == 200, response.text
    path = vault / response.json()["path"]
    first = path.read_text(encoding="utf-8")
    assert f"ai_write_workflow: {retro.id}" in first
    assert "ai_write_skill: export-approved-learning" in first
    assert client.post(f"/api/retrospectives/{retro.id}/export", json=command).status_code == 200
    assert path.read_text(encoding="utf-8") == first
    # Reconcile a crash after the write but before saving the retrospective outcome.
    app.state.repository.save("retrospective", retro.model_dump())
    assert client.post(f"/api/retrospectives/{retro.id}/export", json=command).status_code == 200
    assert path.read_text(encoding="utf-8") == first


def test_uncertain_export_requires_reconciliation_instead_of_rewrite(application, tmp_path):
    from amauxboze.control_plane.contracts import Retrospective
    app, client = application
    vault = tmp_path / "vault"
    vault.mkdir()
    cfg = client.get("/api/settings").json()
    cfg["vault_path"] = str(vault)
    client.put("/api/settings", json=cfg)
    retro = Retrospective(id=str(uuid4()), title="Reviewed learning", run_ids=[], participant_ids=["elena"], mode="live", status="closed")
    app.state.repository.save("retrospective", retro.model_dump())
    action_id = f"learning:{retro.id}"
    path = f"Learnings/Retrospectives/{retro.id}.md"
    app.state.repository.command("knowledge-export:" + action_id, {"retrospective_id": retro.id, "path": path}, [("action", {"id": action_id, "status": "pending", "path": path})], action_id)
    response = client.post(f"/api/retrospectives/{retro.id}/export", json={"revision": 0, "idempotency_key": str(uuid4())})
    assert response.status_code == 409
    assert "reconciliation required" in response.text
    assert not (vault / path).exists()


def test_agent_language_default_validation_and_restart(tmp_path):
    runtime = tmp_path / "language-runtime"
    app = create_app(runtime_path=runtime)
    # Legacy settings migrate through the typed default without rewriting artifacts.
    app.state.repository.save("settings", {"id": "app", "vault_path": str(tmp_path)})
    with TestClient(app) as client:
        cfg = client.get("/api/settings").json()
        assert cfg["agent_language"] == "de"
        assert client.put("/api/settings", json={**cfg, "agent_language": "unknown"}).status_code == 422
        assert client.put("/api/settings", json={**cfg, "agent_language": "en"}).json()["agent_language"] == "en"
    with TestClient(create_app(runtime_path=runtime)) as client:
        cfg = client.get("/api/settings").json()
        assert cfg["agent_language"] == "en"
        assert client.put("/api/settings", json={**cfg, "agent_language": "de"}).status_code == 200
