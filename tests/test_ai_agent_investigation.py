from sqlmodel import Session, select
from app.db.database import engine
from app.services.simulator import ProductionSimulator
from app.services.investigation.agent import AutonomousInvestigationAgent
from app.models.investigation import Investigation, InvestigationStatus


def test_autonomous_ai_agent_investigation_loop():
    with Session(engine) as session:
        # 1. Inject a failure scenario (DB Connection Pool Exhaustion)
        sim = ProductionSimulator(session)
        inj = sim.inject_failure_scenario("db_connection_pool_exhaustion")
        incident_id = inj["incident_id"]

        # 2. Run Autonomous AI Investigation
        agent = AutonomousInvestigationAgent(session)
        result = agent.run_investigation(incident_id)

        assert result["status"] == InvestigationStatus.COMPLETED
        assert result["confidence_score"] >= 0.85
        assert "QueuePool" in result["root_cause"] or "database" in result["root_cause"].lower()
        assert result["tool_calls_count"] >= 4
        assert result["hypotheses_count"] >= 2
        assert result["proposed_remediation_id"] is not None

        # 3. Verify Investigation Record in DB
        inv = session.get(Investigation, result["investigation_id"])
        assert inv is not None
        assert inv.status == InvestigationStatus.COMPLETED
