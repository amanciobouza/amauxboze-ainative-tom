from __future__ import annotations

import json
from pathlib import PurePosixPath
from typing import Any

from amauxboze.adapters import ObsidianAdapter


class CustomerFeedbackPersistence:
    def __init__(self, obsidian: ObsidianAdapter):
        self.obsidian = obsidian

    @staticmethod
    def workspace(workflow_id: str) -> str:
        return str(PurePosixPath("Customers") / "Feedback" / workflow_id)

    def persist_artifact(self, *, workflow_id: str, artifact_type: str, agent_id: str, skill_id: str, content: dict[str, Any]) -> None:
        path = f"{self.workspace(workflow_id)}/{artifact_type}.md"
        payload = json.dumps(content, ensure_ascii=False, indent=2)
        body = f"# {artifact_type.replace('_', ' ').title()}\n\n{payload}\n"
        self.obsidian.write_text(path, body, workflow_id=workflow_id, agent_id=agent_id, skill_id=skill_id)

    def persist_decision(self, *, workflow_id: str, decision: str, rationale: str) -> None:
        path = f"{self.workspace(workflow_id)}/decision-feedback.md"
        body = (
            "# Feedback Decision\n\n"
            f"- Approver: Amancio\n"
            f"- Decision: {decision}\n"
            f"- Rationale: {rationale}\n"
        )
        self.obsidian.write_text(path, body, workflow_id=workflow_id, agent_id="amancio", skill_id="founder-approval")
