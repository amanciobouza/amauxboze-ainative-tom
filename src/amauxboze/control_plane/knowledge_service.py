from __future__ import annotations

import json
from pathlib import Path

from amauxboze.adapters import ObsidianAdapter
from amauxboze.contracts import ToolRequest
from amauxboze.platform.tool_gateway import DefaultToolGateway
from .repository import ConflictError


class KnowledgeService:
    def __init__(self, workflows):
        self.workflows = workflows

    def adapter(self):
        root = Path(self.workflows.settings_getter().vault_path).expanduser()
        if not root.is_dir():
            raise FileNotFoundError("Configured Obsidian vault is unavailable; set an existing vault in settings")
        return ObsidianAdapter(root)

    def list(self, query="", scope="", limit=100):
        adapter = self.adapter()
        root = adapter._resolve_inside_vault(scope)
        if not root.is_dir():
            raise ValueError("Knowledge scope must be a folder")
        items = []
        for path in root.rglob("*.md"):
            try:
                safe = adapter._resolve_inside_vault(path)
                if not safe.is_file() or safe.stat().st_size > 500000:
                    continue
                relative = safe.relative_to(adapter.vault_root).as_posix()
                if query and query.lower() not in relative.lower() and query.lower() not in safe.read_text(encoding="utf-8")[:24000].lower():
                    continue
                items.append({"path": relative, "title": safe.stem, "size": safe.stat().st_size})
                if len(items) >= limit:
                    break
            except (PermissionError, OSError, UnicodeError):
                continue
        return {"items": items, "source": "Obsidian", "limit": limit, "available": True}

    def read(self, path):
        adapter = self.adapter()
        safe = adapter._resolve_inside_vault(path)
        if safe.suffix.lower() != ".md":
            raise PermissionError("Only Markdown notes are exposed")
        with safe.open(encoding="utf-8") as note:
            content = note.read(24001)
        return {"path": safe.relative_to(adapter.vault_root).as_posix(), "content": content[:24000], "truncated": len(content) > 24000, "source": "Obsidian"}

    def export(self, retrospective):
        if retrospective.mode != "live" or retrospective.status != "closed":
            raise ValueError("Only closed live retrospectives can be exported; simulation never writes the vault")
        if retrospective.exported_path:
            return retrospective.exported_path
        adapter = self.adapter()
        gateway = DefaultToolGateway(self.workflows.policy)
        path = f"Learnings/Retrospectives/{retrospective.id}.md"
        content = f"# {retrospective.title}\n\nReviewed retrospective and experiment outcomes.\n\n```json\n{json.dumps(retrospective.model_dump(), ensure_ascii=False, indent=2)}\n```\n"
        action_id = f"learning:{retrospective.id}"
        _, claimed = self.workflows.repo.command("knowledge-export:" + action_id, {"retrospective_id": retrospective.id, "path": path}, [("action", {"id": action_id, "status": "pending", "path": path})], action_id)
        if not claimed:
            # A crash may have occurred after the write but before outcome storage.
            # Prove the exact audited write before accepting a replay.
            target = adapter._resolve_inside_vault(path)
            saved = target.read_text(encoding="utf-8") if target.is_file() else ""
            if not saved.startswith(content.rstrip()) or f"ai_write_workflow: {retrospective.id}" not in saved:
                raise ConflictError("Knowledge write outcome uncertain or still in progress; reconciliation required before retry")
            retrospective.exported_path = path
            self.workflows.repo.save("retrospective", retrospective.model_dump())
            self.workflows.repo.save("action", {"id": action_id, "status": "completed", "path": path})
            return path
        gateway.register("obsidian", lambda payload: {"path": str(adapter.write_text(path, content, workflow_id=retrospective.id, agent_id="elena", skill_id="export-approved-learning"))})
        result = gateway.execute(ToolRequest(agent_id="elena", skill_id="export-approved-learning", tool_name="obsidian", mode="write", payload={"path": path}, idempotency_key=f"learning:{retrospective.id}"))
        if result.status != "ok":
            raise RuntimeError(result.error)
        retrospective.exported_path = path
        self.workflows.repo.save("action", {"id": action_id, "status": "completed", "path": path})
        self.workflows.repo.save("retrospective", retrospective.model_dump())
        self.workflows.repo.event(retrospective.id, "knowledge_exported", {"path": path})
        return path
