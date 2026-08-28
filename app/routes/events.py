from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.database import get_session
from app.models.event import IncidentEvent, EventCreate
from app.models.incident import Incident

router = APIRouter(
    prefix="/incidents/{incident_id}/events",
    tags=["events"],
)


@router.post("/", response_model=IncidentEvent)
def create_event(
    incident_id: str,
    payload: EventCreate,
    session: Session = Depends(get_session),
):
    incident = session.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    event = IncidentEvent(
        id=str(uuid4()),
        incident_id=incident_id,
        event_type=payload.event_type,
        source=payload.source,
        message=payload.message,
        timestamp=payload.timestamp or datetime.now(timezone.utc),
        data=payload.data or {},
    )

    session.add(event)
    session.commit()
    session.refresh(event)

    return event


@router.get("/", response_model=List[IncidentEvent])
def get_events(
    incident_id: str,
    session: Session = Depends(get_session),
):
    incident = session.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    statement = (
        select(IncidentEvent)
        .where(IncidentEvent.incident_id == incident_id)
        .order_by(IncidentEvent.timestamp.asc())
    )

    return session.exec(statement).all()