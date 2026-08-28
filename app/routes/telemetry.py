from datetime import datetime, timezone, timedelta
from typing import List, Optional
from uuid import uuid4
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from app.db.database import get_session
from app.models.telemetry import (
    TelemetryLog,
    TelemetryMetric,
    LogCreate,
    MetricCreate,
    LogLevel,
)

router = APIRouter(
    prefix="/telemetry",
    tags=["telemetry"],
)


@router.get("/metrics", response_model=List[TelemetryMetric])
def query_metrics(
    service: Optional[str] = None,
    metric_name: Optional[str] = None,
    minutes: int = Query(default=30, ge=1, le=1440),
    session: Session = Depends(get_session),
):
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(minutes=minutes)

    query = select(TelemetryMetric).where(TelemetryMetric.timestamp >= window_start)
    if service:
        query = query.where(TelemetryMetric.service == service)
    if metric_name:
        query = query.where(TelemetryMetric.metric_name == metric_name)

    return session.exec(query.order_by(TelemetryMetric.timestamp.asc())).all()


@router.post("/metrics", response_model=TelemetryMetric)
def record_metric(
    payload: MetricCreate,
    session: Session = Depends(get_session),
):
    metric = TelemetryMetric(
        id=str(uuid4()),
        service=payload.service,
        metric_name=payload.metric_name,
        value=payload.value,
        unit=payload.unit,
        timestamp=payload.timestamp or datetime.now(timezone.utc),
    )
    session.add(metric)
    session.commit()
    session.refresh(metric)
    return metric


@router.get("/logs", response_model=List[TelemetryLog])
def query_logs(
    service: Optional[str] = None,
    level: Optional[LogLevel] = None,
    search: Optional[str] = None,
    minutes: int = Query(default=30, ge=1, le=1440),
    limit: int = Query(default=50, ge=1, le=500),
    session: Session = Depends(get_session),
):
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(minutes=minutes)

    query = select(TelemetryLog).where(TelemetryLog.timestamp >= window_start)
    if service:
        query = query.where(TelemetryLog.service == service)
    if level:
        query = query.where(TelemetryLog.level == level)

    logs = session.exec(query.order_by(TelemetryLog.timestamp.desc()).limit(limit)).all()
    if search:
        s_lower = search.lower()
        logs = [l for l in logs if s_lower in l.message.lower()]

    return logs


@router.post("/logs", response_model=TelemetryLog)
def record_log(
    payload: LogCreate,
    session: Session = Depends(get_session),
):
    log = TelemetryLog(
        id=str(uuid4()),
        service=payload.service,
        level=payload.level,
        message=payload.message,
        timestamp=payload.timestamp or datetime.now(timezone.utc),
        trace_id=payload.trace_id,
        metadata_json=payload.metadata or {},
    )
    session.add(log)
    session.commit()
    session.refresh(log)
    return log
