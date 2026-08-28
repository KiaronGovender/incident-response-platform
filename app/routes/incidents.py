from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlmodel import Session, select

from app.db.database import get_session
from app.models.incident import (
    Incident,
    IncidentCreate,
    IncidentSeverity,
    IncidentStatus,
    IncidentUpdate,
)
from app.models.event import IncidentEvent
from app.models.investigation import Investigation, InvestigationToolCall
from app.models.remediation import RemediationAction
from app.services.investigation.agent import AutonomousInvestigationAgent

router = APIRouter(
    prefix="/incidents",
    tags=["incidents"],
)


@router.post("/", response_model=Incident)
def create_incident(
    payload: IncidentCreate,
    session: Session = Depends(get_session),
):
    now = datetime.now(timezone.utc)
    incident = Incident(
        id=f"inc_{uuid4().hex[:8]}",
        title=payload.title,
        description=payload.description,
        service=payload.service,
        severity=payload.severity,
        status=IncidentStatus.OPEN,
        detection_time=now,
        created_at=now,
        updated_at=now,
    )

    session.add(incident)
    session.commit()
    session.refresh(incident)

    return incident


@router.get("/", response_model=List[Incident])
def get_incidents(
    status: Optional[IncidentStatus] = None,
    severity: Optional[IncidentSeverity] = None,
    service: Optional[str] = None,
    session: Session = Depends(get_session),
):
    query = select(Incident)

    if status:
        query = query.where(Incident.status == status)
    if severity:
        query = query.where(Incident.severity == severity)
    if service:
        query = query.where(Incident.service == service)

    return session.exec(query.order_by(Incident.created_at.desc())).all()


@router.get("/{incident_id}", response_model=Incident)
def get_incident(
    incident_id: str,
    session: Session = Depends(get_session),
):
    incident = session.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.patch("/{incident_id}", response_model=Incident)
def update_incident(
    incident_id: str,
    payload: IncidentUpdate,
    session: Session = Depends(get_session),
):
    incident = session.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(incident, key, value)

    incident.updated_at = datetime.now(timezone.utc)
    if payload.status == IncidentStatus.RESOLVED and not incident.resolved_at:
        incident.resolved_at = datetime.now(timezone.utc)

    session.add(incident)
    session.commit()
    session.refresh(incident)
    return incident


@router.post("/{incident_id}/investigate")
def trigger_investigation(
    incident_id: str,
    session: Session = Depends(get_session),
):
    incident = session.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    agent = AutonomousInvestigationAgent(session)
    result = agent.run_investigation(incident_id)
    return result


@router.get("/{incident_id}/timeline")
def get_incident_timeline(
    incident_id: str,
    session: Session = Depends(get_session),
):
    incident = session.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Fetch events
    events = session.exec(
        select(IncidentEvent)
        .where(IncidentEvent.incident_id == incident_id)
        .order_by(IncidentEvent.timestamp.asc())
    ).all()

    timeline_items = []

    # Add Incident Creation
    timeline_items.append({
        "type": "INCIDENT_CREATED",
        "timestamp": incident.created_at.isoformat(),
        "title": f"Incident Created: {incident.title}",
        "severity": incident.severity,
        "details": incident.description,
        "source": "platform",
    })

    # Add Events
    for e in events:
        timeline_items.append({
            "type": f"EVENT_{e.event_type.upper()}",
            "timestamp": e.timestamp.isoformat(),
            "title": f"[{e.source}] {e.message}",
            "details": e.data,
            "source": e.source,
        })

    # Add Investigation Tool Executions
    investigation = session.exec(
        select(Investigation).where(Investigation.incident_id == incident_id)
    ).first()

    if investigation:
        tool_calls = session.exec(
            select(InvestigationToolCall)
            .where(InvestigationToolCall.investigation_id == investigation.id)
            .order_by(InvestigationToolCall.timestamp.asc())
        ).all()

        for tc in tool_calls:
            timeline_items.append({
                "type": "AGENT_TOOL_CALL",
                "timestamp": tc.timestamp.isoformat(),
                "title": f"Agent Executed Tool: {tc.tool_name}",
                "details": {"parameters": tc.parameters, "rationale": tc.rationale},
                "source": "ai-agent",
            })

    # Add Remediation Actions
    remediations = session.exec(
        select(RemediationAction)
        .where(RemediationAction.incident_id == incident_id)
        .order_by(RemediationAction.created_at.asc())
    ).all()

    for r in remediations:
        timeline_items.append({
            "type": f"REMEDIATION_{r.status.upper()}",
            "timestamp": (r.executed_at or r.created_at).isoformat(),
            "title": f"Remediation Action: {r.title} ({r.status})",
            "details": {
                "risk_level": r.risk_level,
                "output": r.execution_output,
                "verification": r.verification_result,
            },
            "source": "remediation-engine",
        })

    # Sort chronological
    timeline_items.sort(key=lambda x: x["timestamp"])

    return {
        "incident_id": incident_id,
        "incident_title": incident.title,
        "status": incident.status,
        "timeline": timeline_items,
    }