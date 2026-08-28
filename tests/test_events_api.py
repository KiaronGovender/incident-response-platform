from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_incident_events_lifecycle():
    # 1. Create an incident first
    inc_resp = client.post(
        "/incidents/",
        json={
            "title": "Auth Service 500 Spike",
            "description": "Auth service throwing unhandled exceptions",
            "service": "auth-service",
            "severity": "critical",
        },
    )
    assert inc_resp.status_code == 200
    incident_id = inc_resp.json()["id"]

    # 2. Add an event
    event_payload = {
        "event_type": "alert",
        "source": "pagerduty",
        "message": "Elevated error rate alert triggered",
        "data": {"alert_id": "AL-9910", "threshold": "5%"},
    }
    event_resp = client.post(f"/incidents/{incident_id}/events/", json=event_payload)
    assert event_resp.status_code == 200
    event_data = event_resp.json()
    assert event_data["incident_id"] == incident_id
    assert event_data["event_type"] == "alert"
    assert event_data["data"]["alert_id"] == "AL-9910"

    # 3. Retrieve events for this incident
    list_resp = client.get(f"/incidents/{incident_id}/events/")
    assert list_resp.status_code == 200
    events = list_resp.json()
    assert len(events) >= 1
    assert any(e["message"] == "Elevated error rate alert triggered" for e in events)
