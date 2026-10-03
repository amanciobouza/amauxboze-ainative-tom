from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .models import SkillManifest
from .schema_validation import validate_against_schema


class SkillRegistry:
    def __init__(self, manifest_root: str | Path):
        self.manifest_root = Path(manifest_root)
        self._skills: dict[str, SkillManifest] = {}

    def load(self) -> dict[str, SkillManifest]:
        skills: dict[str, SkillManifest] = {}
        for path in sorted(self.manifest_root.glob("*/skill.yaml")):
            if path.parent.name.startswith("_"):
                continue
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            manifest = SkillManifest.model_validate(raw)
            if manifest.id in skills:
                raise ValueError(f"Duplicate skill id: {manifest.id}")
            if not manifest.version.strip():
                raise ValueError(f"Skill '{manifest.id}' must declare a version")
            skills[manifest.id] = manifest
        self._skills = skills
        return skills

    def get(self, skill_id: str) -> SkillManifest:
        try:
            return self._skills[skill_id]
        except KeyError as exc:
            raise KeyError(f"Unknown skill: {skill_id}") from exc

    def validate_input(self, skill_id: str, payload: dict[str, Any]) -> None:
        skill = self.get(skill_id)
        validate_against_schema(payload, skill.inputs, label="input")

    def validate_output(self, skill_id: str, payload: dict[str, Any]) -> None:
        skill = self.get(skill_id)
        validate_against_schema(payload, skill.outputs, label="output")
