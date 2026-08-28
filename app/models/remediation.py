from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel
from pydantic import BaseModel


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RemediationStatus(str, Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"
    EXECUTED = "executed"
    VERIFIED = "verified"
    FAILED = "failed"


class RemediationAction(SQLModel, table=True):
    id: str = Field(primary_key=True)
    incident_id: str = Field(index=True)
    action_type: str  # rollback, restart, scale, failover, config_change
    title: str
    description: str
    risk_level: RiskLevel = RiskLevel.MEDIUM
    status: RemediationStatus = RemediationStatus.PROPOSED
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
    )
    approved_by: Optional[str] = None
    execution_output: Optional[str] = None
    verification_result: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    executed_at: Optional[datetime] = None


class RemediationApproval(BaseModel):
    approved_by: str = "oncall-engineer"
    execute_now: bool = True
