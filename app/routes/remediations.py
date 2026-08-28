from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.database import get_session
from app.models.remediation import RemediationAction, RemediationApproval
from app.services.remediation import RemediationService

router = APIRouter(
    prefix="/remediations",
    tags=["remediations"],
)


@router.get("/", response_model=List[RemediationAction])
def list_remediations(
    session: Session = Depends(get_session),
):
    return session.exec(select(RemediationAction).order_by(RemediationAction.created_at.desc())).all()


@router.get("/incident/{incident_id}", response_model=List[RemediationAction])
def get_remediations_by_incident(
    incident_id: str,
    session: Session = Depends(get_session),
):
    return session.exec(
        select(RemediationAction)
        .where(RemediationAction.incident_id == incident_id)
        .order_by(RemediationAction.created_at.desc())
    ).all()


@router.get("/{action_id}", response_model=RemediationAction)
def get_remediation_action(
    action_id: str,
    session: Session = Depends(get_session),
):
    action = session.get(RemediationAction, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Remediation action not found")
    return action


@router.post("/{action_id}/approve")
def approve_action(
    action_id: str,
    payload: RemediationApproval = RemediationApproval(),
    session: Session = Depends(get_session),
):
    service = RemediationService(session)
    try:
        return service.approve_action(
            action_id=action_id,
            approved_by=payload.approved_by,
            execute_now=payload.execute_now,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{action_id}/reject")
def reject_action(
    action_id: str,
    rejected_by: str = "oncall-engineer",
    session: Session = Depends(get_session),
):
    service = RemediationService(session)
    try:
        return service.reject_action(action_id=action_id, rejected_by=rejected_by)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{action_id}/execute")
def execute_action(
    action_id: str,
    session: Session = Depends(get_session),
):
    service = RemediationService(session)
    try:
        return service.execute_action(action_id=action_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{action_id}/verify")
def verify_action(
    action_id: str,
    session: Session = Depends(get_session),
):
    service = RemediationService(session)
    try:
        return service.verify_remediation(action_id=action_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
