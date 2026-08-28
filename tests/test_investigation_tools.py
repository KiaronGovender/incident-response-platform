from sqlmodel import Session
from app.db.database import engine
from app.services.investigation.tools import (
    query_logs,
    query_metrics,
    get_recent_deployments,
    get_service_dependencies,
    inspect_database_health,
)


def test_investigation_diagnostic_tools():
    with Session(engine) as session:
        # 1. Query logs
        logs = query_logs(session, "payment-api", limit=10)
        assert "logs" in logs
        assert isinstance(logs["logs"], list)

        # 2. Query metrics
        metrics = query_metrics(session, "payment-api")
        assert "metrics_summary" in metrics

        # 3. Get recent deployments
        deps = get_recent_deployments(session, "payment-api")
        assert "deployments" in deps

        # 4. Service dependencies
        topology = get_service_dependencies(session, "payment-api")
        assert topology["service"] == "payment-api"
        assert "dependencies" in topology

        # 5. Database health
        db = inspect_database_health(session)
        assert "database" in db
        assert "active_connections" in db
