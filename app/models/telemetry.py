from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel
from pydantic import BaseModel


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class TelemetryMetric(SQLModel, table=True):
    id: str = Field(primary_key=True)
    service: str = Field(index=True)
    metric_name: str = Field(index=True)
    value: float
    unit: str = "count"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)


class TelemetryLog(SQLModel, table=True):
    id: str = Field(primary_key=True)
    service: str = Field(index=True)
    level: LogLevel = LogLevel.INFO
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    trace_id: Optional[str] = None
    metadata_json: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column("metadata", JSON),
    )


class MetricCreate(BaseModel):
    service: str
    metric_name: str
    value: float
    unit: str = "count"
    timestamp: Optional[datetime] = None


class LogCreate(BaseModel):
    service: str
    level: LogLevel = LogLevel.INFO
    message: str
    timestamp: Optional[datetime] = None
    trace_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
