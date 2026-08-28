from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from sqlalchemy import Column, String
from sqlmodel import Field, SQLModel
from pydantic import BaseModel, ConfigDict


class IncidentSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    MITIGATING = "mitigating"
    RESOLVED = "resolved"


class IncidentBase(SQLModel):
    model_config = ConfigDict(use_enum_values=True)
    title: str
    description: str
    service: str
    severity: IncidentSeverity = Field(
        default=IncidentSeverity.MEDIUM,
        sa_column=Column(String, default="medium"),
    )
    status: IncidentStatus = Field(
        default=IncidentStatus.OPEN,
        sa_column=Column(String, default="open"),
    )
    root_cause: Optional[str] = None
    resolution_summary: Optional[str] = None
    confidence_score: Optional[float] = None


class Incident(IncidentBase, table=True):
    id: str = Field(primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    detection_time: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


class IncidentCreate(BaseModel):
    title: str
    description: str
    service: str
    severity: IncidentSeverity = IncidentSeverity.MEDIUM


class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    service: Optional[str] = None
    severity: Optional[IncidentSeverity] = None
    status: Optional[IncidentStatus] = None
    root_cause: Optional[str] = None
    resolution_summary: Optional[str] = None
    confidence_score: Optional[float] = None