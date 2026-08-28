import random
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from uuid import uuid4
from sqlmodel import Session, select

from app.models.service import Service, ServiceStatus
from app.models.deployment import Deployment, DeploymentStatus
from app.models.telemetry import TelemetryLog, TelemetryMetric, LogLevel
from app.models.event import IncidentEvent, EventType
from app.models.incident import Incident, IncidentSeverity, IncidentStatus


FAILURE_SCENARIOS = {
    "db_connection_pool_exhaustion": {
        "id": "db_connection_pool_exhaustion",
        "title": "Database Connection Pool Saturation & Exhaustion",
        "service": "payment-api",
        "severity": "critical",
        "description": "After recent deployment v2.4.1, database connection checkout requests fail due to unmanaged sessions, causing severe latency and 500 error spikes.",
        "expected_root_cause": "Deployment v2.4.1 introduced a database connection leak in the payment transaction handler, exhausting the PostgreSQL connection pool (QueuePool limit reached).",
        "expected_remediation": "Roll back payment-api deployment to v2.4.0 and restart service pods to clear orphan connection handles.",
    },
    "memory_leak": {
        "id": "memory_leak",
        "title": "Memory Saturation & Out-Of-Memory CrashLoop",
        "service": "order-service",
        "severity": "high",
        "description": "Order processing worker memory consumption grows unbounded, leading to severe heap pressure and pod OOM crashes.",
        "expected_root_cause": "Unbounded caching buffer in the order synchronization pipeline causing progressive heap memory growth until OOMKilled.",
        "expected_remediation": "Restart order-service pods to reclaim leaked memory and apply horizontal pod autoscaling.",
    },
    "bad_deployment_regression": {
        "id": "bad_deployment_regression",
        "title": "Authentication Token Parser Regression (v1.8.3)",
        "service": "auth-service",
        "severity": "critical",
        "description": "Newly deployed version v1.8.3 fails to validate JWT tokens missing the optional audience claim, causing 45% of incoming login requests to crash.",
        "expected_root_cause": "Null pointer exception introduced in auth-service v1.8.3 during JWT claim parsing without fallback defaults.",
        "expected_remediation": "Roll back auth-service deployment to stable version v1.8.2.",
    },
    "downstream_dependency_failure": {
        "id": "downstream_dependency_failure",
        "title": "External Payment Provider 503 Outage",
        "service": "payment-api",
        "severity": "high",
        "description": "Third-party payment gateway provider is returning 503 Service Unavailable and socket connection timeouts on transaction settlement.",
        "expected_root_cause": "Third-party external payment processor infrastructure outage causing egress request timeouts.",
        "expected_remediation": "Activate secondary payment processor fallback routing and open circuit breaker.",
    },
    "latency_spike_cascade": {
        "id": "latency_spike_cascade",
        "title": "Notification Queue Saturation & Latency Cascade",
        "service": "notification-service",
        "severity": "medium",
        "description": "Notification dispatch worker backlog saturates Redis message queue, cascading thread pool delays upstream to API Gateway.",
        "expected_root_cause": "Redis message queue worker starvation causing thread pool blocking on synchronous notification dispatch.",
        "expected_remediation": "Scale notification worker concurrency and switch to asynchronous background delivery mode.",
    },
}


class ProductionSimulator:
    """
    Simulates production microservices environment, generating realistic telemetry
    and supporting reproducible incident failure injection scenarios.
    """

    def __init__(self, session: Session):
        self.session = session

    def get_available_scenarios(self) -> List[Dict[str, Any]]:
        return list(FAILURE_SCENARIOS.values())

    def inject_failure_scenario(self, scenario_id: str) -> Dict[str, Any]:
        if scenario_id not in FAILURE_SCENARIOS:
            raise ValueError(f"Unknown scenario ID: {scenario_id}")

        scenario = FAILURE_SCENARIOS[scenario_id]
        service_name = scenario["service"]
        now = datetime.now(timezone.utc)

        # 1. Update Service Health
        service = self.session.exec(select(Service).where(Service.name == service_name)).first()
        if service:
            service.status = ServiceStatus.FAILING
            self.session.add(service)

        # 2. Inject Scenario-specific Deployment & Telemetry
        if scenario_id == "db_connection_pool_exhaustion":
            # Add bad deployment if not present
            bad_dep = Deployment(
                id=str(uuid4()),
                service="payment-api",
                version="v2.4.1",
                commit_hash="e4f5g6h",
                deployed_by="github-actions",
                status=DeploymentStatus.SUCCESSFUL,
                timestamp=now - timedelta(minutes=8),
                changes_summary="Refactored database query execution pipeline",
                rollback_version="v2.4.0",
            )
            self.session.add(bad_dep)

            # Generate anomalous metrics
            metrics = [
                TelemetryMetric(id=str(uuid4()), service="payment-api", metric_name="error_rate", value=22.4, unit="percent", timestamp=now - timedelta(minutes=4)),
                TelemetryMetric(id=str(uuid4()), service="payment-api", metric_name="request_latency_p99", value=4250.0, unit="ms", timestamp=now - timedelta(minutes=4)),
                TelemetryMetric(id=str(uuid4()), service="payment-api", metric_name="db_connection_pool_usage", value=100.0, unit="percent", timestamp=now - timedelta(minutes=4)),
                TelemetryMetric(id=str(uuid4()), service="payment-api", metric_name="cpu_usage", value=48.2, unit="percent", timestamp=now - timedelta(minutes=4)),
                TelemetryMetric(id=str(uuid4()), service="postgres-db", metric_name="active_connections", value=99.0, unit="count", timestamp=now - timedelta(minutes=4)),
            ]
            for m in metrics:
                self.session.add(m)

            # Generate error & critical logs
            logs = [
                TelemetryLog(
                    id=str(uuid4()),
                    service="payment-api",
                    level=LogLevel.WARN,
                    message="Database connection checkout duration exceeded 1000ms threshold for /api/v1/charge",
                    timestamp=now - timedelta(minutes=6),
                    trace_id="tr_10928301",
                    metadata_json={"endpoint": "/api/v1/charge", "latency_ms": 1120},
                ),
                TelemetryLog(
                    id=str(uuid4()),
                    service="payment-api",
                    level=LogLevel.ERROR,
                    message="TimeoutError: QueuePool limit of size 20 overflow 10 reached, connection timed out after 30.00 seconds",
                    timestamp=now - timedelta(minutes=4),
                    trace_id="tr_10928399",
                    metadata_json={"error": "QueuePoolLimitReached", "pool_size": 20, "overflow": 10},
                ),
                TelemetryLog(
                    id=str(uuid4()),
                    service="payment-api",
                    level=LogLevel.CRITICAL,
                    message="HTTP 500 Internal Server Error rate spike detected: 22.4% over past 5m window",
                    timestamp=now - timedelta(minutes=3),
                    trace_id="tr_10928410",
                    metadata_json={"http_status": 500, "service": "payment-api"},
                ),
            ]
            for l in logs:
                self.session.add(l)

        elif scenario_id == "memory_leak":
            metrics = [
                TelemetryMetric(id=str(uuid4()), service="order-service", metric_name="memory_usage", value=94.5, unit="percent", timestamp=now - timedelta(minutes=3)),
                TelemetryMetric(id=str(uuid4()), service="order-service", metric_name="error_rate", value=16.8, unit="percent", timestamp=now - timedelta(minutes=3)),
                TelemetryMetric(id=str(uuid4()), service="order-service", metric_name="request_latency_p99", value=3100.0, unit="ms", timestamp=now - timedelta(minutes=3)),
            ]
            for m in metrics:
                self.session.add(m)

            logs = [
                TelemetryLog(
                    id=str(uuid4()),
                    service="order-service",
                    level=LogLevel.ERROR,
                    message="java.lang.OutOfMemoryError: Java heap space during order buffer dispatch",
                    timestamp=now - timedelta(minutes=3),
                    trace_id="tr_mem_001",
                    metadata_json={"error": "OutOfMemoryError", "heap_used_mb": 4096},
                ),
                TelemetryLog(
                    id=str(uuid4()),
                    service="order-service",
                    level=LogLevel.CRITICAL,
                    message="Pod order-service-7f8d9b-xc41 crashed with exit status 137 (OOMKilled)",
                    timestamp=now - timedelta(minutes=2),
                    trace_id="tr_mem_002",
                    metadata_json={"k8s_reason": "OOMKilled"},
                ),
            ]
            for l in logs:
                self.session.add(l)

        elif scenario_id == "bad_deployment_regression":
            bad_dep = Deployment(
                id=str(uuid4()),
                service="auth-service",
                version="v1.8.3",
                commit_hash="bad9911",
                deployed_by="github-actions",
                status=DeploymentStatus.SUCCESSFUL,
                timestamp=now - timedelta(minutes=10),
                changes_summary="Refactored JWT claims validation logic",
                rollback_version="v1.8.2",
            )
            self.session.add(bad_dep)

            metrics = [
                TelemetryMetric(id=str(uuid4()), service="auth-service", metric_name="error_rate", value=45.2, unit="percent", timestamp=now - timedelta(minutes=5)),
                TelemetryMetric(id=str(uuid4()), service="auth-service", metric_name="request_latency_p99", value=950.0, unit="ms", timestamp=now - timedelta(minutes=5)),
            ]
            for m in metrics:
                self.session.add(m)

            logs = [
                TelemetryLog(
                    id=str(uuid4()),
                    service="auth-service",
                    level=LogLevel.ERROR,
                    message="NullPointerException: Cannot invoke 'String.equals(Object)' because audClaim is null at TokenParser.java:84",
                    timestamp=now - timedelta(minutes=6),
                    trace_id="tr_auth_01",
                    metadata_json={"exception": "NullPointerException", "file": "TokenParser.java", "line": 84},
                ),
                TelemetryLog(
                    id=str(uuid4()),
                    service="auth-service",
                    level=LogLevel.CRITICAL,
                    message="Authentication verification failure rate 45.2% exceeds critical threshold (5%)",
                    timestamp=now - timedelta(minutes=4),
                    trace_id="tr_auth_02",
                    metadata_json={"alert": "AuthServiceElevatedErrors"},
                ),
            ]
            for l in logs:
                self.session.add(l)

        elif scenario_id == "downstream_dependency_failure":
            metrics = [
                TelemetryMetric(id=str(uuid4()), service="payment-api", metric_name="error_rate", value=38.0, unit="percent", timestamp=now - timedelta(minutes=4)),
                TelemetryMetric(id=str(uuid4()), service="payment-api", metric_name="external_dependency_latency", value=10200.0, unit="ms", timestamp=now - timedelta(minutes=4)),
            ]
            for m in metrics:
                self.session.add(m)

            logs = [
                TelemetryLog(
                    id=str(uuid4()),
                    service="payment-api",
                    level=LogLevel.ERROR,
                    message="HTTP 503 Service Unavailable received from external gateway https://api.stripe.com/v1/charges (timeout after 10000ms)",
                    timestamp=now - timedelta(minutes=4),
                    trace_id="tr_ext_01",
                    metadata_json={"upstream": "api.stripe.com", "status": 503},
                ),
            ]
            for l in logs:
                self.session.add(l)

        elif scenario_id == "latency_spike_cascade":
            metrics = [
                TelemetryMetric(id=str(uuid4()), service="notification-service", metric_name="error_rate", value=8.5, unit="percent", timestamp=now - timedelta(minutes=3)),
                TelemetryMetric(id=str(uuid4()), service="notification-service", metric_name="request_latency_p99", value=4800.0, unit="ms", timestamp=now - timedelta(minutes=3)),
                TelemetryMetric(id=str(uuid4()), service="notification-service", metric_name="queue_depth", value=14500.0, unit="messages", timestamp=now - timedelta(minutes=3)),
            ]
            for m in metrics:
                self.session.add(m)

            logs = [
                TelemetryLog(
                    id=str(uuid4()),
                    service="notification-service",
                    level=LogLevel.WARN,
                    message="Notification dispatch queue backlog reached 14,500 messages, thread pool saturation imminent",
                    timestamp=now - timedelta(minutes=3),
                    trace_id="tr_notif_01",
                    metadata_json={"queue_depth": 14500},
                ),
            ]
            for l in logs:
                self.session.add(l)

        # 3. Create Incident Record
        incident = Incident(
            id=f"inc_{uuid4().hex[:8]}",
            title=f"[{service_name.upper()}] {scenario['title']}",
            description=scenario["description"],
            service=service_name,
            severity=IncidentSeverity(scenario["severity"]),
            status=IncidentStatus.OPEN,
            detection_time=now,
            created_at=now,
            updated_at=now,
        )
        self.session.add(incident)

        # 4. Attach Alert & Initial Evidence Events
        events = [
            IncidentEvent(
                id=str(uuid4()),
                incident_id=incident.id,
                event_type=EventType.ALERT,
                source="prometheus-alertmanager",
                message=f"CRITICAL: High error rate & anomaly threshold breached on service {service_name}",
                timestamp=now - timedelta(minutes=3),
                data={"alert_name": f"{service_name}_HighErrorRate", "severity": scenario["severity"]},
            ),
            IncidentEvent(
                id=str(uuid4()),
                incident_id=incident.id,
                event_type=EventType.METRIC,
                source="datadog-agent",
                message=f"Service {service_name} error rate breached SLA threshold",
                timestamp=now - timedelta(minutes=3),
                data={"service": service_name, "scenario_id": scenario_id},
            ),
        ]
        for e in events:
            self.session.add(e)

        self.session.commit()
        self.session.refresh(incident)

        return {
            "scenario": scenario,
            "incident_id": incident.id,
            "status": "injected",
            "message": f"Successfully injected failure scenario: {scenario['title']}",
        }

    def reset_environment(self) -> Dict[str, Any]:
        """Resets all services to healthy status and adds healthy baseline metrics."""
        services = self.session.exec(select(Service)).all()
        for s in services:
            s.status = ServiceStatus.HEALTHY
            self.session.add(s)

        now = datetime.now(timezone.utc)
        for s in services:
            self.session.add(TelemetryMetric(id=str(uuid4()), service=s.name, metric_name="error_rate", value=random.uniform(0.1, 0.6), unit="percent", timestamp=now))
            self.session.add(TelemetryMetric(id=str(uuid4()), service=s.name, metric_name="request_latency_p99", value=random.uniform(45.0, 110.0), unit="ms", timestamp=now))
            self.session.add(TelemetryMetric(id=str(uuid4()), service=s.name, metric_name="cpu_usage", value=random.uniform(20.0, 45.0), unit="percent", timestamp=now))

        self.session.commit()
        return {"status": "reset", "message": "Environment reset to healthy production baseline."}
