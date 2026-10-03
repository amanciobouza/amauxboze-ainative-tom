from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from threading import Lock


class ObsidianAdapter:
    def __init__(self, vault_root: str | Path):
        self.vault_root = Path(vault_root).expanduser().resolve()
        self._write_lock = Lock()

    def _resolve_inside_vault(self, relative_path: str | Path) -> Path:
        candidate = (self.vault_root / Path(relative_path)).resolve()
        try:
            candidate.relative_to(self.vault_root)
        except ValueError as exc:
            raise PermissionError("Path escapes configured Obsidian vault") from exc
        return candidate

    def read_text(self, relative_path: str | Path) -> str:
        path = self._resolve_inside_vault(relative_path)
        return path.read_text(encoding="utf-8")

    def write_text(
        self,
        relative_path: str | Path,
        content: str,
        *,
        workflow_id: str,
        agent_id: str,
        skill_id: str,
    ) -> Path:
        path = self._resolve_inside_vault(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        stamp = datetime.now(timezone.utc).isoformat()
        audit = (
            "\n\n---\n"
            f"ai_write_workflow: {workflow_id}\n"
            f"ai_write_agent: {agent_id}\n"
            f"ai_write_skill: {skill_id}\n"
            f"ai_write_timestamp: {stamp}\n"
        )

        with self._write_lock:
            tmp = path.with_suffix(path.suffix + ".tmp")
            tmp.write_text(content.rstrip() + audit, encoding="utf-8")
            tmp.replace(path)

        return path
