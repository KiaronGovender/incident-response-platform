from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_simulator_scenarios():
    # 1. List scenarios
    list_resp = client.get("/simulator/scenarios")
    assert list_resp.status_code == 200
    scenarios = list_resp.json()
    assert len(scenarios) >= 5
    scenario_ids = [s["id"] for s in scenarios]
    assert "db_connection_pool_exhaustion" in scenario_ids
    assert "memory_leak" in scenario_ids
    assert "bad_deployment_regression" in scenario_ids

    # 2. Inject a scenario
    inject_resp = client.post(
        "/simulator/inject",
        json={"scenario_id": "db_connection_pool_exhaustion", "auto_investigate": False},
    )
    assert inject_resp.status_code == 200
    inject_data = inject_resp.json()
    assert inject_data["injection"]["status"] == "injected"
    assert "incident_id" in inject_data["injection"]

    # 3. Reset environment
    reset_resp = client.post("/simulator/reset")
    assert reset_resp.status_code == 200
    assert reset_resp.json()["status"] == "reset"
