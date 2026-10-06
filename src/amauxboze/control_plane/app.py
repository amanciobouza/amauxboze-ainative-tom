from __future__ import annotations

import asyncio
import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .catalog import DEPARTMENTS, PROCESSES, organization
from .contracts import AppSettings, DecisionCommand, ExperimentResult, RetrospectiveStart, RunCommand, StartCommand, now
from .knowledge_service import KnowledgeService
from .model_transport import LiveModelGateway, model_status, validate_settings
from .read_models import agent_activity, dashboard
from .repository import ConflictError, SQLiteRepository
from .retrospective_service import RetrospectiveService
from .workflow_service import WorkflowService, safe_error


ROOT = Path(__file__).resolve().parents[3]


def create_app(root: Path = ROOT, runtime_path: Path | None = None, gateway_factory=LiveModelGateway):
    runtime = runtime_path or Path(os.getenv("TOM_RUNTIME_PATH", str(root / ".runtime")))
    runtime.mkdir(parents=True, exist_ok=True)
    load_dotenv(root / ".env", override=False)
    repo = SQLiteRepository(runtime / "runtime.sqlite")
    default = AppSettings(vault_path=os.getenv("OBSIDIAN_VAULT_PATH", r"C:\Users\amanc\OneDrive\ObsidianVaults\Amaux Bozé"), lm_studio_url=os.getenv("LM_STUDIO_BASE_URL", "http://127.0.0.1:1234"))

    def settings():
        try:
            return AppSettings.model_validate({k: v for k, v in repo.get("settings", "app").items() if k != "id"})
        except KeyError:
            return default

    service = WorkflowService(root, repo, runtime, settings, gateway_factory)
    retros = RetrospectiveService(service)
    knowledge = KnowledgeService(service)

    @asynccontextmanager
    async def lifespan(app):
        service.recover()
        retros.recover()
        yield
        retros.close()
        service.close()
        repo.close()

    app = FastAPI(title="Amaux Bozé TOM/OS", version="0.2.0", lifespan=lifespan)
    app.state.workflows, app.state.retrospectives, app.state.repository = service, retros, repo
    origins = ["http://127.0.0.1:3000", "http://localhost:3000", "http://127.0.0.1:5173", "http://localhost:5173", "http://127.0.0.1:8000", "http://localhost:8000"]
    app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET", "POST", "PUT"], allow_headers=["Content-Type", "Last-Event-ID"])
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "[::1]", "testserver"])

    @app.middleware("http")
    async def local_origin(request, call_next):
        origin = request.headers.get("origin")
        if request.method not in {"GET", "HEAD", "OPTIONS"} and origin and origin not in origins:
            return JSONResponse(status_code=403, content={"error": {"code": "origin_forbidden", "message": "Mutation origin is not an allowed local app"}})
        return await call_next(request)

    async def error_handler(request, exc):
        status = 409 if isinstance(exc, ConflictError) else 403 if isinstance(exc, PermissionError) else 404 if isinstance(exc, (KeyError, FileNotFoundError)) else 422 if isinstance(exc, ValueError) else 503
        return JSONResponse(status_code=status, content={"error": {"code": type(exc).__name__, "message": safe_error(exc)}})

    for error_type in (ConflictError, PermissionError, KeyError, FileNotFoundError, ValueError, RuntimeError):
        app.add_exception_handler(error_type, error_handler)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        return JSONResponse(status_code=422, content={"error": {"code": "validation", "message": "Eingaben ungültig", "fields": [{"path": ".".join(map(str, e["loc"])), "message": e["msg"]} for e in exc.errors()]}})

    @app.get("/api/health")
    def health():
        return {"status": "ok", "application": "Amaux Bozé TOM/OS", "timestamp": now(), "database": "ready", "knowledge_available": Path(settings().vault_path).is_dir(), "publishing": "not_configured", "local_only": settings().privacy == "local_only"}

    @app.get("/api/dashboard")
    def get_dashboard(mode: str = Query("live", pattern="^(live|simulation)$"), days: int = Query(7, ge=1, le=365)):
        return dashboard(repo, mode, days)

    @app.get("/api/organization")
    def get_organization():
        return organization(service.agents)

    @app.get("/api/agents")
    def agents():
        return [{**a.model_dump(), "activity": agent_activity(service, a.id).model_dump(), "department_ids": [d.id for d in DEPARTMENTS if a.id in d.member_ids]} for a in service.agents.load().values()]

    @app.get("/api/agents/{identity}")
    def agent(identity: str, offset: int = Query(0, ge=0), limit: int = Query(30, ge=1, le=100), status: str | None = None):
        profile = service.agents.get(identity)
        registered_skills = service.skills.load()
        bio = root / "agents" / f"{profile.id}.md"
        history = [a for a in repo.list("attempt") if a["agent_id"] == identity and (not status or a["status"] == status)]
        return {**profile.model_dump(), "biography": bio.read_text(encoding="utf-8") if bio.is_file() else None, "biography_source": f"agents/{profile.id}.md" if bio.is_file() else None, "skill_details": [registered_skills[s].model_dump() for s in profile.skills if s in registered_skills], "unavailable_skills": [s for s in profile.skills if s not in registered_skills], "activity": agent_activity(service, identity).model_dump(), "history": history[offset:offset + limit], "history_total": len(history)}

    @app.get("/api/skills")
    def skills():
        return [s.model_dump() for s in service.skills.load().values()]

    @app.get("/api/skills/{identity}")
    def skill(identity: str):
        return service.skills.get(identity)

    @app.get("/api/processes")
    def processes():
        return PROCESSES

    @app.post("/api/runs", status_code=202)
    def start(command: StartCommand):
        return service.start(command)

    @app.get("/api/runs")
    def runs(status: str | None = None, mode: str | None = None, process_id: str | None = None, offset: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100)):
        rows = repo.list("run")
        if status == "active":
            rows = [r for r in rows if r["status"] in {"queued", "running", "held", "waiting_approval"}]
        elif status:
            rows = [r for r in rows if r["status"] == status]
        rows = [r for r in rows if (not mode or r["mode"] == mode) and (not process_id or r["process_id"] == process_id)]
        return {"items": rows[offset:offset + limit], "total": len(rows), "offset": offset}

    @app.get("/api/runs/{identity}")
    def run(identity: str):
        value = service.get(identity)
        return {**value.model_dump(), "attempts": [a for a in repo.list("attempt") if a["run_id"] == identity], "events": repo.events(run_id=identity), "approval": repo.get("approval", value.approval_id) if value.approval_id else None}

    @app.post("/api/runs/{identity}/{action}")
    def run_command(identity: str, action: str, command: RunCommand):
        return service.command(identity, action, command)

    @app.get("/api/approvals")
    def approvals():
        return [a for a in repo.list("approval") if a["status"] == "pending"]

    @app.post("/api/approvals/{identity}/decision")
    def decide(identity: str, command: DecisionCommand):
        return service.decide(identity, command)

    @app.get("/api/events")
    def events(after: int = Query(0, ge=0), run_id: str | None = None):
        return repo.events(after=after, run_id=run_id)

    @app.get("/api/events/stream")
    async def stream(request: Request, after: int = Query(0, ge=0)):
        async def generate():
            cursor = max(after, int(request.headers.get("last-event-id", "0")))
            while not await request.is_disconnected():
                rows = repo.events(after=cursor)
                for row in rows:
                    cursor = row["id"]
                    yield f"id: {cursor}\nevent: runtime\ndata: {json.dumps(row, ensure_ascii=False)}\n\n"
                if not rows:
                    yield ": heartbeat\n\n"
                await asyncio.sleep(1)
        return StreamingResponse(generate(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    @app.get("/api/knowledge")
    def notes(q: str = Query("", max_length=200), scope: str = "", limit: int = Query(100, ge=1, le=200)):
        return knowledge.list(q, scope, limit)

    @app.get("/api/knowledge/note")
    def note(path: str):
        return knowledge.read(path)

    @app.get("/api/models")
    def models():
        return model_status(settings())

    @app.get("/api/settings")
    def get_settings():
        return settings()

    @app.put("/api/settings")
    def save_settings(value: AppSettings):
        validate_settings(value)
        repo.save("settings", {"id": "app", **value.model_dump()})
        repo.event("system", "settings_updated", {"provider": value.provider, "privacy": value.privacy})
        return value

    @app.get("/api/retrospectives")
    def retrospective_list():
        return repo.list("retrospective")

    @app.post("/api/retrospectives", status_code=202)
    def retrospective_start(command: RetrospectiveStart):
        return retros.start(command)

    @app.get("/api/retrospectives/{identity}")
    def retrospective(identity: str):
        return retros.get(identity)

    @app.post("/api/retrospectives/{identity}/review")
    def retrospective_review(identity: str, command: DecisionCommand):
        return retros.review(identity, command)

    @app.post("/api/retrospectives/{identity}/experiments/{experiment_id}/start")
    def experiment_start(identity: str, experiment_id: str, command: RunCommand):
        return retros.experiment_start(identity, experiment_id, command)

    @app.post("/api/retrospectives/{identity}/experiments/{experiment_id}/result")
    def experiment_result(identity: str, experiment_id: str, command: ExperimentResult):
        return retros.evaluate(identity, experiment_id, command)

    @app.post("/api/retrospectives/{identity}/export")
    def export(identity: str, command: RunCommand):
        retro = retros.get(identity)
        if retro.revision != command.revision:
            raise ConflictError("Retrospective revision changed")
        return {"path": knowledge.export(retro)}

    @app.get("/{path:path}", include_in_schema=False)
    def frontend(path: str):
        if path.startswith("api/"):
            return JSONResponse({"error": {"code": "not_found", "message": "Unknown API route"}}, status_code=404)
        dist = root / "web/dist"
        target = (dist / path).resolve()
        if target.is_relative_to(dist.resolve()) and target.is_file():
            return FileResponse(target)
        if (dist / "index.html").is_file():
            return FileResponse(dist / "index.html")
        return JSONResponse({"message": "Frontend build missing. Start run-local.ps1."}, status_code=404)

    return app


def application():
    return create_app()
