from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from pydantic import BaseModel

from app.db.database import get_session
from app.services.simulator import ProductionSimulator
from app.services.detection import DetectionEngine

router = APIRouter(
    prefix="/simulator",
    tags=["simulator"],
)


class InjectScenarioRequest(BaseModel):
    scenario_id: str
    auto_investigate: bool = True


@router.get("/scenarios")
def list_scenarios(
    session: Session = Depends(get_session),
) -> List[Dict[str, Any]]:
    sim = ProductionSimulator(session)
    return sim.get_available_scenarios()


@router.post("/inject")
def inject_scenario(
    payload: InjectScenarioRequest,
    session: Session = Depends(get_session),
) -> Dict[str, Any]:
    sim = ProductionSimulator(session)
    try:
        inject_res = sim.inject_failure_scenario(payload.scenario_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Trigger detection
    detector = DetectionEngine(session)
    detection_res = detector.scan_all_services()

    # If auto_investigate, trigger AI investigation immediately
    investigation_res = None
    if payload.auto_investigate and inject_res.get("incident_id"):
        from app.services.investigation.agent import AutonomousInvestigationAgent
        agent = AutonomousInvestigationAgent(session)
        investigation_res = agent.run_investigation(inject_res["incident_id"])

    return {
        "injection": inject_res,
        "detection": detection_res,
        "investigation": investigation_res,
    }


@router.post("/reset")
def reset_environment(
    session: Session = Depends(get_session),
) -> Dict[str, Any]:
    sim = ProductionSimulator(session)
    return sim.reset_environment()
