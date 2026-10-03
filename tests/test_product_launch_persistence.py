from pathlib import Path

from amauxboze.adapters import ObsidianAdapter
from amauxboze.workflows.product_launch_persistence import ProductLaunchPersistence


def test_persists_launch_artifact_and_decision(tmp_path: Path):
    persistence = ProductLaunchPersistence(ObsidianAdapter(tmp_path))
    persistence.persist_artifact(
        workflow_id="launch-1",
        artifact_type="launch_brief",
        agent_id="elena",
        skill_id="define-launch-brief",
        content={"objective": "Launch watch"},
    )
    persistence.persist_decision(
        workflow_id="launch-1",
        decision="approve",
        rationale="Ready to launch",
    )

    artifact = tmp_path / "Products" / "Launches" / "launch-1" / "launch_brief.md"
    decision = tmp_path / "Products" / "Launches" / "launch-1" / "decision-launch.md"
    assert artifact.exists()
    assert decision.exists()
    assert "Launch watch" in artifact.read_text(encoding="utf-8")
    assert "Ready to launch" in decision.read_text(encoding="utf-8")
