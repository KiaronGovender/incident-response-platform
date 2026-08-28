from sqlmodel import Session
from app.db.database import engine
from app.services.detection import DetectionEngine
from app.models.telemetry import TelemetryMetric
from app.models.incident import Incident
from datetime import datetime, timezone
from uuid import uuid4


def test_detection_engine_triggers_on_threshold_breach():
    with Session(engine) as session:
        # Ingest an anomalous metric (error rate 28.5%)
        metric = TelemetryMetric(
            id=str(uuid4()),
            service="order-service",
            metric_name="error_rate",
            value=28.5,
            unit="percent",
            timestamp=datetime.now(timezone.utc),
        )
        session.add(metric)
        session.commit()

        # Run detection
        engine_svc = DetectionEngine(session)
        result = engine_svc.evaluate_service_health("order-service")

        assert result is not None
        assert result["action"] in ["created_incident", "correlated_to_existing"]
        assert len(result["violations"]) >= 1

        # Check incident was created or correlated
        incident = session.get(Incident, result["incident_id"])
        assert incident is not None
        assert incident.service == "order-service"
