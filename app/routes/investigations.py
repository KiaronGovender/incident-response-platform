from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.database import get_session
from app.models.investigation import (
    Investigation,
    InvestigationHypothesis,
    InvestigationToolCall,
    InvestigationDetailResponse,
)

router = APIRouter(
    prefix="/investigations",
    tags=["investigations"],
)


@router.get("/{investigation_id}", response_model=InvestigationDetailResponse)
def get_investigation_detail(
    investigation_id: str,
    session: Session = Depends(get_session),
):
    investigation = session.get(Investigation, investigation_id)
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")

    hypotheses = session.exec(
        select(InvestigationHypothesis)
        .where(InvestigationHypothesis.investigation_id == investigation_id)
        .order_by(InvestigationHypothesis.confidence.desc())
    ).all()

    tool_calls = session.exec(
        select(InvestigationToolCall)
        .where(InvestigationToolCall.investigation_id == investigation_id)
        .order_by(InvestigationToolCall.step_index.asc())
    ).all()

    return InvestigationDetailResponse(
        investigation=investigation,
        hypotheses=hypotheses,
        tool_calls=tool_calls,
    )


@router.get("/incident/{incident_id}", response_model=Optional[InvestigationDetailResponse])
def get_investigation_by_incident(
    incident_id: str,
    session: Session = Depends(get_session),
):
    investigation = session.exec(
        select(Investigation)
        .where(Investigation.incident_id == incident_id)
        .order_by(Investigation.created_at.desc())
    ).first()

    if not investigation:
        return None

    hypotheses = session.exec(
        select(InvestigationHypothesis)
        .where(InvestigationHypothesis.investigation_id == investigation.id)
        .order_by(InvestigationHypothesis.confidence.desc())
    ).all()

    tool_calls = session.exec(
        select(InvestigationToolCall)
        .where(InvestigationToolCall.investigation_id == investigation.id)
        .order_by(InvestigationToolCall.step_index.asc())
    ).all()

    return InvestigationDetailResponse(
        investigation=investigation,
        hypotheses=hypotheses,
        tool_calls=tool_calls,
    )
