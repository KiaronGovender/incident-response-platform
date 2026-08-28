from typing import List, Optional
from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel
from pydantic import BaseModel


class Runbook(SQLModel, table=True):
    id: str = Field(primary_key=True)
    title: str
    service: str = Field(index=True)
    trigger_patterns: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
    )
    diagnosis_steps: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
    )
    remediation_actions: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
    )
    risk_level: str = "medium"
    content: str
    tags: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
    )


class PastIncident(SQLModel, table=True):
    id: str = Field(primary_key=True)
    title: str
    service: str = Field(index=True)
    root_cause: str
    resolution: str
    symptoms: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
    )
    postmortem_url: Optional[str] = None


class KnowledgeSearchQuery(BaseModel):
    query: str
    service: Optional[str] = None
    top_k: int = 3
