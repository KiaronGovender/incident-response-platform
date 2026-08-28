from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_and_get_incident():
    # 1. Create Incident
    payload = {
        "title": "Payment API Latency Surge",
        "description": "P99 latency elevated beyond 3000ms",
        "service": "payment-api",
        "severity": "high",
    }
    create_resp = client.post("/incidents/", json=payload)
    assert create_resp.status_code == 200
    incident = create_resp.json()
    assert incident["id"].startswith("inc_")
    assert incident["title"] == payload["title"]
    assert incident["service"] == payload["service"]
    assert incident["status"] == "open"

    # 2. Get Incident by ID
    get_resp = client.get(f"/incidents/{incident['id']}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == incident["id"]

    # 3. List Incidents with filter
    list_resp = client.get("/incidents/?service=payment-api")
    assert list_resp.status_code == 200
    incidents_list = list_resp.json()
    assert len(incidents_list) >= 1
    assert any(i["id"] == incident["id"] for i in incidents_list)

    # 4. Patch Incident
    patch_resp = client.patch(
        f"/incidents/{incident['id']}",
        json={"status": "investigating", "root_cause": "Preliminary testing"},
    )
    assert patch_resp.status_code == 200
    updated = patch_resp.json()
    assert updated["status"] == "investigating"
    assert updated["root_cause"] == "Preliminary testing"

    # 5. Get Timeline
    timeline_resp = client.get(f"/incidents/{incident['id']}/timeline")
    assert timeline_resp.status_code == 200
    timeline = timeline_resp.json()
    assert "timeline" in timeline
    assert len(timeline["timeline"]) >= 1
