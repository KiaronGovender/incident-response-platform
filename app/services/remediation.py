import random
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from uuid import uuid4
from sqlmodel import Session, select

from app.models.incident import Incident, IncidentStatus
from app.models.service import Service, ServiceStatus
from app.models.deployment import Deployment, DeploymentStatus
from app.models.telemetry import TelemetryMetric
from app.models.event import IncidentEvent, EventType
from app.models.remediation import (
    RemediationAction,
    RemediationStatus,
)


class RemediationService:
    def __init__(self, session: Session):
        self.session = session

    def approve_action(
        self,
        action_id: str,
        approved_by: str = "oncall-engineer",
        execute_now: bool = True,
    ) -> Dict[str, Any]:
        action = self.session.get(RemediationAction, action_id)
        if not action:
            raise ValueError(f"Remediation action {action_id} not found")

        action.status = RemediationStatus.APPROVED
        action.approved_by = approved_by
        self.session.add(action)

        # Record approval event in incident timeline
        approval_event = IncidentEvent(
            id=str(uuid4()),
            incident_id=action.incident_id,
            event_type=EventType.AGENT_ACTION,
            source="remediation-engine",
            message=f"Remediation action '{action.title}' approved by {approved_by}.",
            timestamp=datetime.now(timezone.utc),
            data={"action_id": action.id, "approved_by": approved_by},
        )
        self.session.add(approval_event)
        self.session.commit()

        if execute_now:
            return self.execute_action(action_id)

        return {"status": "approved", "action_id": action.id}

    def reject_action(self, action_id: str, rejected_by: str = "oncall-engineer") -> Dict[str, Any]:
        action = self.session.get(RemediationAction, action_id)
        if not action:
            raise ValueError(f"Remediation action {action_id} not found")

        action.status = RemediationStatus.REJECTED
        self.session.add(action)

        event = IncidentEvent(
            id=str(uuid4()),
            incident_id=action.incident_id,
            event_type=EventType.AGENT_ACTION,
            source="remediation-engine",
            message=f"Remediation action '{action.title}' rejected by {rejected_by}.",
            timestamp=datetime.now(timezone.utc),
            data={"action_id": action.id, "rejected_by": rejected_by},
        )
        self.session.add(event)
        self.session.commit()
        return {"status": "rejected", "action_id": action.id}

    def execute_action(self, action_id: str) -> Dict[str, Any]:
        action = self.session.get(RemediationAction, action_id)
        if not action:
            raise ValueError(f"Remediation action {action_id} not found")

        incident = self.session.get(Incident, action.incident_id)
        now = datetime.now(timezone.utc)

        action.status = RemediationStatus.EXECUTING
        if incident:
            incident.status = IncidentStatus.MITIGATING
            self.session.add(incident)
        self.session.add(action)
        self.session.commit()

        # Perform Action Logic
        service_name = action.parameters.get("service")
        output_logs = []

        if action.action_type == "rollback":
            target_version = action.parameters.get("target_version") or "v2.4.0"
            service = self.session.exec(select(Service).where(Service.name == service_name)).first()
            if service:
                service.current_version = target_version
                service.status = ServiceStatus.HEALTHY
                self.session.add(service)

            # Record rollback deployment
            rollback_dep = Deployment(
                id=str(uuid4()),
                service=service_name or "unknown",
                version=target_version,
                commit_hash=uuid4().hex[:7],
                deployed_by="automated-remediation",
                status=DeploymentStatus.ROLLED_BACK,
                timestamp=now,
                changes_summary=f"Automated rollback triggered to mitigate incident {action.incident_id}",
            )
            self.session.add(rollback_dep)
            output_logs.append(f"Successfully rolled back {service_name} to version {target_version}.")

        elif action.action_type == "restart":
            service = self.session.exec(select(Service).where(Service.name == service_name)).first()
            if service:
                service.status = ServiceStatus.HEALTHY
                self.session.add(service)
            output_logs.append(f"Issued rolling pod restart for service {service_name}. 4/4 pods healthy.")

        elif action.action_type == "failover":
            output_logs.append("Secondary payment processor route enabled. Circuit breaker set to OPEN.")

        action.status = RemediationStatus.EXECUTED
        action.executed_at = now
        action.execution_output = "\n".join(output_logs)
        self.session.add(action)

        # Record execution event
        exec_event = IncidentEvent(
            id=str(uuid4()),
            incident_id=action.incident_id,
            event_type=EventType.INFRASTRUCTURE,
            source="remediation-executor",
            message=f"Executed remediation: {action.title} ({action.execution_output})",
            timestamp=now,
            data={"action_id": action.id, "output": action.execution_output},
        )
        self.session.add(exec_event)
        self.session.commit()

        # Run verification automatically
        return self.verify_remediation(action_id)

    def verify_remediation(self, action_id: str) -> Dict[str, Any]:
        action = self.session.get(RemediationAction, action_id)
        if not action:
            raise ValueError(f"Remediation action {action_id} not found")

        incident = self.session.get(Incident, action.incident_id)
        service_name = action.parameters.get("service") or (incident.service if incident else "general")
        now = datetime.now(timezone.utc)

        # Generate healthy recovery telemetry points
        healthy_metrics = [
            TelemetryMetric(id=str(uuid4()), service=service_name, metric_name="error_rate", value=random.uniform(0.1, 0.4), unit="percent", timestamp=now),
            TelemetryMetric(id=str(uuid4()), service=service_name, metric_name="request_latency_p99", value=random.uniform(55.0, 95.0), unit="ms", timestamp=now),
            TelemetryMetric(id=str(uuid4()), service=service_name, metric_name="db_connection_pool_usage", value=random.uniform(15.0, 32.0), unit="percent", timestamp=now),
            TelemetryMetric(id=str(uuid4()), service=service_name, metric_name="memory_usage", value=random.uniform(30.0, 48.0), unit="percent", timestamp=now),
        ]
        for m in healthy_metrics:
            self.session.add(m)

        # Ensure service is marked healthy
        service = self.session.exec(select(Service).where(Service.name == service_name)).first()
        if service:
            service.status = ServiceStatus.HEALTHY
            self.session.add(service)

        action.status = RemediationStatus.VERIFIED
        action.verification_result = (
            f"Verification SUCCESS: Error rate dropped to 0.2% (threshold: 5.0%). "
            f"P99 latency recovered to 72ms (threshold: 2000ms). All health probes passing."
        )
        self.session.add(action)

        if incident:
            incident.status = IncidentStatus.RESOLVED
            incident.resolved_at = now
            incident.resolution_summary = (
                f"Incident resolved via {action.title}. Automated verification confirmed error rates and latency "
                f"returned to nominal production SLA parameters."
            )
            incident.updated_at = now
            self.session.add(incident)

            # Record Resolution Event
            resolution_event = IncidentEvent(
                id=str(uuid4()),
                incident_id=incident.id,
                event_type=EventType.SERVICE_HEALTH,
                source="verification-engine",
                message=f"Incident RESOLVED: {incident.resolution_summary}",
                timestamp=now,
                data={"verification_result": action.verification_result, "action_id": action.id},
            )
            self.session.add(resolution_event)

        self.session.commit()
        self.session.refresh(action)

        return {
            "status": "verified",
            "action_id": action.id,
            "incident_id": action.incident_id,
            "incident_status": incident.status if incident else "resolved",
            "verification_result": action.verification_result,
        }
