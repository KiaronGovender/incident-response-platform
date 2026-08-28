from sqlmodel import Session
from app.db.database import engine
from app.services.simulator import ProductionSimulator
from app.services.investigation.agent import AutonomousInvestigationAgent
from app.services.remediation import RemediationService
from app.models.remediation import RemediationAction, RemediationStatus
from app.models.incident import Incident, IncidentStatus


def test_remediation_approval_execution_and_verification():
    with Session(engine) as session:
        # 1. Inject failure & run investigation
        sim = ProductionSimulator(session)
        inj = sim.inject_failure_scenario("bad_deployment_regression")
        incident_id = inj["incident_id"]

        agent = AutonomousInvestigationAgent(session)
        inv_res = agent.run_investigation(incident_id)
        action_id = inv_res["proposed_remediation_id"]

        # 2. Approve and Execute Remediation Action
        rem_svc = RemediationService(session)
        approve_res = rem_svc.approve_action(action_id, approved_by="senior-sre@example.com", execute_now=True)

        assert approve_res["status"] == "verified"
        assert "Verification SUCCESS" in approve_res["verification_result"]

        # 3. Check Incident is now RESOLVED
        incident = session.get(Incident, incident_id)
        assert incident.status == IncidentStatus.RESOLVED
        assert incident.resolved_at is not None
        assert incident.resolution_summary is not None
