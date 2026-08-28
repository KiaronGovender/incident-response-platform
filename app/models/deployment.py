from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel
from pydantic import BaseModel


class DeploymentStatus(str, Enum):
    SUCCESSFUL = "successful"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class Deployment(SQLModel, table=True):
    id: str = Field(primary_key=True)
    service: str = Field(index=True)
    version: str
    commit_hash: str
    deployed_by: str = "github-actions"
    status: DeploymentStatus = DeploymentStatus.SUCCESSFUL
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    changes_summary: Optional[str] = None
    rollback_version: Optional[str] = None


class DeploymentCreate(BaseModel):
    service: str
    version: str
    commit_hash: str
    deployed_by: str = "github-actions"
    status: DeploymentStatus = DeploymentStatus.SUCCESSFUL
    changes_summary: Optional[str] = None
    rollback_version: Optional[str] = None
