from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from uuid import uuid4
from sqlmodel import Session, select

from app.models.incident import Incident, IncidentSeverity, IncidentStatus
from app.models.event import IncidentEvent, EventType
from app.models.telemetry import TelemetryMetric, TelemetryLog, LogLevel
from app.models.service import Service, ServiceStatus


THRESHOLDS = {
    "error_rate": {"threshold": 5.0, "severity": IncidentSeverity.HIGH, "unit": "%"},
    "request_latency_p99": {"threshold": 2000.0, "severity": IncidentSeverity.HIGH, "unit": "ms"},
    "db_connection_pool_usage": {"threshold": 85.0, "severity": IncidentSeverity.CRITICAL, "unit": "%"},
    "memory_usage": {"threshold": 90.0, "severity": IncidentSeverity.HIGH, "unit": "%"},
}


class DetectionEngine:
    def __init__(self, session: Session):
        self.session = session

    def evaluate_service_health(self, service_name: str) -> Optional[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(minutes=15)

        # Query recent metrics for service
        metrics = self.session.exec(
            select(TelemetryMetric).where(
                TelemetryMetric.service == service_name,
                TelemetryMetric.timestamp >= window_start,
            )
        ).all()

        violations = []
        max_severity = IncidentSeverity.MEDIUM

        for m in metrics:
            if m.metric_name in THRESHOLDS:
                rule = THRESHOLDS[m.metric_name]
                if m.value >= rule["threshold"]:
                    violations.append({
                        "metric": m.metric_name,
                        "value": m.value,
                        "threshold": rule["threshold"],
                        "unit": rule["unit"],
                    })
                    if rule["severity"] == IncidentSeverity.CRITICAL:
                        max_severity = IncidentSeverity.CRITICAL
                    elif rule["severity"] == IncidentSeverity.HIGH and max_severity != IncidentSeverity.CRITICAL:
                        max_severity = IncidentSeverity.HIGH

        # Check for recent critical logs
        critical_logs = self.session.exec(
            select(TelemetryLog).where(
                TelemetryLog.service == service_name,
                TelemetryLog.level.in_([LogLevel.ERROR, LogLevel.CRITICAL]),
                TelemetryLog.timestamp >= window_start,
            )
        ).all()

        if not violations and len(critical_logs) == 0:
            return None

        # Check if there is already an open incident for this service
        existing_incident = self.session.exec(
            select(Incident).where(
                Incident.service == service_name,
                Incident.status.in_([IncidentStatus.OPEN, IncidentStatus.INVESTIGATING, IncidentStatus.MITIGATING]),
            )
        ).first()

        if existing_incident:
            # Correlate event into existing incident
            event = IncidentEvent(
                id=str(uuid4()),
                incident_id=existing_incident.id,
                event_type=EventType.ALERT,
                source="detection-engine",
                message=f"Detection engine detected ongoing threshold violations on {service_name}: {violations}",
                timestamp=now,
                data={"violations": violations, "critical_logs_count": len(critical_logs)},
            )
            self.session.add(event)
            self.session.commit()
            return {
                "action": "correlated_to_existing",
                "incident_id": existing_incident.id,
                "violations": violations,
            }

        # Create new Incident
        title = f"Automated Alert: {service_name} SLA Violation"
        if violations:
            main_v = violations[0]
            title = f"{service_name}: {main_v['metric']} exceeded ({main_v['value']}{main_v['unit']})"

        incident = Incident(
            id=f"inc_{uuid4().hex[:8]}",
            title=title,
            description=f"Automated detection engine detected {len(violations)} metric threshold breaches and {len(critical_logs)} critical log errors on service {service_name}.",
            service=service_name,
            severity=max_severity,
            status=IncidentStatus.OPEN,
            detection_time=now,
            created_at=now,
            updated_at=now,
        )
        self.session.add(incident)

        # Update service status
        service = self.session.exec(select(Service).where(Service.name == service_name)).first()
        if service:
            service.status = ServiceStatus.FAILING if max_severity == IncidentSeverity.CRITICAL else ServiceStatus.DEGRADED
            self.session.add(service)

        # Attach initial alert event
        alert_event = IncidentEvent(
            id=str(uuid4()),
            incident_id=incident.id,
            event_type=EventType.ALERT,
            source="detection-engine",
            message=f"Threshold breach detected: {violations}",
            timestamp=now,
            data={"violations": violations, "critical_logs_count": len(critical_logs)},
        )
        self.session.add(alert_event)

        self.session.commit()
        self.session.refresh(incident)

        return {
            "action": "created_incident",
            "incident_id": incident.id,
            "violations": violations,
        }

    def scan_all_services(self) -> List[Dict[str, Any]]:
        services = self.session.exec(select(Service)).all()
        results = []
        for s in services:
            res = self.evaluate_service_health(s.name)
            if res:
                results.append(res)
        return results
