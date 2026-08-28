from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from sqlalchemy import Column, JSON, String
from sqlmodel import Field, SQLModel
from pydantic import BaseModel, ConfigDict


class EventType(str, Enum):
    LOG = "log"
    METRIC = "metric"
    ALERT = "alert"
    DEPLOYMENT = "deployment"
    INFRASTRUCTURE = "infrastructure"
    CONFIGURATION = "configuration"
    DATABASE = "database"
    SERVICE_HEALTH = "service_health"
    AGENT_ACTION = "agent_action"


class IncidentEvent(SQLModel, table=True):
    model_config = ConfigDict(use_enum_values=True)
    id: str = Field(primary_key=True)
    incident_id: str = Field(index=True)
    event_type: EventType = Field(
        sa_column=Column(String, nullable=False),
    )
    source: str
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
    )


class EventCreate(BaseModel):
    event_type: EventType
    source: str
    message: str
    timestamp: Optional[datetime] = None
    data: Optional[Dict[str, Any]] = None