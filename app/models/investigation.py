from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel
from pydantic import BaseModel


class InvestigationStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class HypothesisStatus(str, Enum):
    EXPLORING = "exploring"
    CONFIRMED = "confirmed"
    REFUTED = "refuted"


class Investigation(SQLModel, table=True):
    id: str = Field(primary_key=True)
    incident_id: str = Field(index=True)
    status: InvestigationStatus = InvestigationStatus.PENDING
    current_hypothesis: Optional[str] = None
    confidence_score: Optional[float] = None
    root_cause: Optional[str] = None
    summary: Optional[str] = None
    recommended_remediation: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InvestigationHypothesis(SQLModel, table=True):
    id: str = Field(primary_key=True)
    investigation_id: str = Field(index=True)
    hypothesis: str
    status: HypothesisStatus = HypothesisStatus.EXPLORING
    confidence: float = 0.0
    reasoning: Optional[str] = None
    supporting_evidence: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
    )
    refuting_evidence: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InvestigationToolCall(SQLModel, table=True):
    id: str = Field(primary_key=True)
    investigation_id: str = Field(index=True)
    step_index: int = 0
    tool_name: str
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
    )
    result: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
    )
    rationale: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InvestigationDetailResponse(BaseModel):
    investigation: Investigation
    hypotheses: List[InvestigationHypothesis]
    tool_calls: List[InvestigationToolCall]
