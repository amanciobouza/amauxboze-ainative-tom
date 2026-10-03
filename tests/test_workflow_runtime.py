from amauxboze.workflows import SideEffectGuard, WorkflowRuntime

def test_workflow_id_is_unique():
    one = WorkflowRuntime.new_workflow_id()
    two = WorkflowRuntime.new_workflow_id()
    assert one != two
    assert one.startswith("wf-")

def test_side_effect_guard_runs_once():
    guard = SideEffectGuard()
    calls = []

    def side_effect():
        calls.append("called")
        return "ok"

    assert guard.run_once("publish:1", side_effect) == "ok"
    assert guard.run_once("publish:1", side_effect) is None
    assert calls == ["called"]
