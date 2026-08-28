from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.database import get_session
from app.models.knowledge import Runbook, PastIncident, KnowledgeSearchQuery
from app.services.investigation.rag import RAGKnowledgeService

router = APIRouter(
    prefix="/knowledge",
    tags=["knowledge"],
)


@router.get("/runbooks", response_model=List[Runbook])
def list_runbooks(
    service: Optional[str] = None,
    session: Session = Depends(get_session),
):
    query = select(Runbook)
    if service:
        query = query.where(Runbook.service == service)
    return session.exec(query).all()


@router.get("/runbooks/{runbook_id}", response_model=Runbook)
def get_runbook(
    runbook_id: str,
    session: Session = Depends(get_session),
):
    rb = session.get(Runbook, runbook_id)
    if not rb:
        raise HTTPException(status_code=404, detail="Runbook not found")
    return rb


@router.get("/past-incidents", response_model=List[PastIncident])
def list_past_incidents(
    service: Optional[str] = None,
    session: Session = Depends(get_session),
):
    query = select(PastIncident)
    if service:
        query = query.where(PastIncident.service == service)
    return session.exec(query).all()


@router.post("/search")
def search_knowledge(
    payload: KnowledgeSearchQuery,
    session: Session = Depends(get_session),
) -> Dict[str, Any]:
    rag = RAGKnowledgeService(session)
    return rag.unified_search(payload.query, service=payload.service)
