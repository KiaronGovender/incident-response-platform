from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.database import get_session
from app.models.service import Service, ServiceCreate

router = APIRouter(
    prefix="/services",
    tags=["services"],
)


@router.get("/", response_model=List[Service])
def list_services(
    session: Session = Depends(get_session),
):
    return session.exec(select(Service)).all()


@router.get("/{service_name}", response_model=Service)
def get_service(
    service_name: str,
    session: Session = Depends(get_session),
):
    service = session.exec(select(Service).where(Service.name == service_name)).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service
