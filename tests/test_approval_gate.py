from amauxboze.workflows.approvals import ApprovalRequest

def test_approval_request_is_explicit():
    request = ApprovalRequest(
        workflow_id="wf-123",
        action="publish_shopify_product",
        reason="External publication requires founder approval",
        summary="Publish product X",
    )
    assert request.action == "publish_shopify_product"
    assert "founder approval" in request.reason
