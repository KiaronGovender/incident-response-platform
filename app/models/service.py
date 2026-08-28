from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel
from pydantic import BaseModel


class ServiceStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"


class Service(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str = Field(unique=True, index=True)
    environment: str = "production"
    owner: str = "core-infra"
    repository: str = "KiaronGovender/incident-response-platform"
    current_version: str = "v1.0.0"
    status: ServiceStatus = ServiceStatus.HEALTHY
    dependencies: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
    )
    health_check_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ServiceCreate(BaseModel):
    id: str
    name: str
    environment: str = "production"
    owner: str = "core-infra"
    repository: str = "KiaronGovender/incident-response-platform"
    current_version: str = "v1.0.0"
    status: ServiceStatus = ServiceStatus.HEALTHY
    dependencies: List[str] = []
    health_check_url: Optional[str] = None
