from __future__ import annotations

from pathlib import Path

import yaml

from .models import SkillManifest


class SkillRegistry:
    def __init__(self, manifest_root: str | Path):
        self.manifest_root = Path(manifest_root)
        self._skills: dict[str, SkillManifest] = {}

    def load(self) -> dict[str, SkillManifest]:
        skills: dict[str, SkillManifest] = {}
        for path in sorted(self.manifest_root.glob("*/skill.yaml")):
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            manifest = SkillManifest.model_validate(raw)
            if manifest.id in skills:
                raise ValueError(f"Duplicate skill id: {manifest.id}")
            skills[manifest.id] = manifest
        self._skills = skills
        return skills

    def get(self, skill_id: str) -> SkillManifest:
        try:
            return self._skills[skill_id]
        except KeyError as exc:
            raise KeyError(f"Unknown skill: {skill_id}") from exc
