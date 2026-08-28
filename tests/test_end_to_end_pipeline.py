from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_full_autonomous_incident_lifecycle_e2e():
    """
    End-to-End Test:
    1. Production simulator injects DB connection pool exhaustion.
    2. Automated detection notices anomaly.
    3. AI agent performs multi-step investigation using telemetry tools and RAG.
    4. SRE views incident timeline & proposed remediation.
    5. SRE approves remediation rollback.
    6. System executes rollback and verifies recovery metrics.
    7. Incident transitions to RESOLVED with postmortem report.
    """
    # 1. Inject Failure Scenario
    inject_resp = client.post(
        "/simulator/inject",
        json={"scenario_id": "db_connection_pool_exhaustion", "auto_investigate": True},
    )
    assert inject_resp.status_code == 200
    inject_data = inject_resp.json()
    incident_id = inject_data["injection"]["incident_id"]
    assert incident_id is not None

    # 2. Verify Investigation completed with Root Cause
    inv_data = inject_data["investigation"]
    assert inv_data is not None
    assert inv_data["confidence_score"] >= 0.85
    action_id = inv_data["proposed_remediation_id"]
    assert action_id is not None

    # 3. Check Incident Details
    inc_resp = client.get(f"/incidents/{incident_id}")
    assert inc_resp.status_code == 200
    inc = inc_resp.json()
    assert inc["status"] == "investigating"
    assert inc["root_cause"] is not None

    # 4. Check Unified Timeline
    timeline_resp = client.get(f"/incidents/{incident_id}/timeline")
    assert timeline_resp.status_code == 200
    timeline = timeline_resp.json()["timeline"]
    assert len(timeline) >= 5
    types = [t["type"] for t in timeline]
    assert "INCIDENT_CREATED" in types
    assert "AGENT_TOOL_CALL" in types
    assert "EVENT_AGENT_ACTION" in types

    # 5. Approve & Execute Remediation
    approve_resp = client.post(
        f"/remediations/{action_id}/approve",
        json={"approved_by": "oncall-lead", "execute_now": True},
    )
    assert approve_resp.status_code == 200
    approval_result = approve_resp.json()
    assert approval_result["status"] == "verified"

    # 6. Verify Incident is RESOLVED
    resolved_inc_resp = client.get(f"/incidents/{incident_id}")
    assert resolved_inc_resp.status_code == 200
    resolved_inc = resolved_inc_resp.json()
    assert resolved_inc["status"] == "resolved"
    assert resolved_inc["resolved_at"] is not None
