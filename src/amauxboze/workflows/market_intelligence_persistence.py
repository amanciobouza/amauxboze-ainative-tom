from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import PurePosixPath
from typing import Any

from amauxboze.adapters import ObsidianAdapter


class MarketIntelligencePersistence:
    def __init__(self, obsidian: ObsidianAdapter):
        self.obsidian = obsidian

    @staticmethod
    def workspace(workflow_id: str) -> str:
        return str(PurePosixPath("Research") / "Intelligence" / workflow_id)

    def persist_artifact(self, *, workflow_id: str, artifact_type: str, agent_id: str, skill_id: str, content: dict[str, Any]) -> None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        path = f"{self.workspace(workflow_id)}/{stamp}-{artifact_type}.md"
        payload = json.dumps(content, ensure_ascii=False, indent=2)
        body = f"# {artifact_type.replace('_', ' ').title()}\n\n{payload}\n"
        self.obsidian.write_text(path, body, workflow_id=workflow_id, agent_id=agent_id, skill_id=skill_id)

    def persist_decision(self, *, workflow_id: str, decision: str, rationale: str) -> None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        path = f"{self.workspace(workflow_id)}/{stamp}-founder-decision.md"
        body = (
            "# Founder Decision\n\n"
            f"- Approver: Amancio\n"
            f"- Decision: {decision}\n"
            f"- Rationale: {rationale}\n"
        )
        self.obsidian.write_text(path, body, workflow_id=workflow_id, agent_id="amancio", skill_id="founder-approval")
