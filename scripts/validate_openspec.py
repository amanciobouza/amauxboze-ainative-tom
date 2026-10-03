from __future__ import annotations

from pathlib import Path
import sys
import yaml


ROOT = Path("openspec")
REQUIRED_CHANGE_FILES = {"proposal.md", "design.md", "tasks.md"}


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def validate() -> None:
    config = ROOT / "config.yaml"
    if not config.exists():
        fail("openspec/config.yaml is missing")

    data = yaml.safe_load(config.read_text(encoding="utf-8"))
    if data.get("schema") != "spec-driven":
        fail("openspec/config.yaml must declare schema: spec-driven")

    changes_dir = ROOT / "changes"
    if not changes_dir.exists():
        fail("openspec/changes is missing")

    change_dirs = [p for p in changes_dir.iterdir() if p.is_dir()]
    if not change_dirs:
        fail("No OpenSpec changes found")

    for change in change_dirs:
        missing = [name for name in REQUIRED_CHANGE_FILES if not (change / name).exists()]
        if missing:
            fail(f"{change.name}: missing {', '.join(missing)}")

        metadata = change / ".openspec.yaml"
        if not metadata.exists():
            fail(f"{change.name}: missing .openspec.yaml")

        meta = yaml.safe_load(metadata.read_text(encoding="utf-8"))
        if meta.get("schema") != "spec-driven":
            fail(f"{change.name}: .openspec.yaml must declare schema: spec-driven")

        specs = change / "specs"
        if not specs.exists():
            fail(f"{change.name}: specs directory is missing")

        spec_files = list(specs.glob("*/spec.md"))
        if not spec_files:
            fail(f"{change.name}: no capability specs found")

    print("OpenSpec validation passed.")


if __name__ == "__main__":
    validate()
