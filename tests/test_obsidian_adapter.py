from pathlib import Path

import pytest

from amauxboze.adapters import ObsidianAdapter


def test_read_and_write_inside_vault(tmp_path: Path):
    adapter = ObsidianAdapter(tmp_path)
    adapter.write_text(
        "Organization/test.md",
        "# Test",
        workflow_id="wf-1",
        agent_id="elena",
        skill_id="prepare-decision",
    )
    content = adapter.read_text("Organization/test.md")
    assert "# Test" in content
    assert "ai_write_workflow: wf-1" in content


def test_blocks_path_escape(tmp_path: Path):
    adapter = ObsidianAdapter(tmp_path)
    with pytest.raises(PermissionError):
        adapter.read_text("../outside.md")
