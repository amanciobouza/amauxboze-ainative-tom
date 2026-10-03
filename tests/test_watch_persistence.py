from pathlib import Path

from amauxboze.adapters import ObsidianAdapter
from amauxboze.workflows.watch_persistence import WatchDevelopmentPersistence


def test_persists_artifact_and_decision(tmp_path: Path):
    adapter = ObsidianAdapter(tmp_path)
    persistence = WatchDevelopmentPersistence(adapter)

    persistence.persist_artifact(
        workflow_id="wf-1",
        artifact_type="product_brief",
        agent_id="elena",
        skill_id="define-product-brief",
        content={"objective": "Create watch"},
    )
    persistence.persist_decision(
        workflow_id="wf-1",
        gate="approve_for_spec",
        decision="approve",
        rationale="Strong fit",
    )

    artifact = tmp_path / "Products" / "Development" / "wf-1" / "product_brief.md"
    decision = tmp_path / "Products" / "Development" / "wf-1" / "decision-approve_for_spec.md"

    assert artifact.exists()
    assert decision.exists()
    assert "Create watch" in artifact.read_text(encoding="utf-8")
    assert "Strong fit" in decision.read_text(encoding="utf-8")
