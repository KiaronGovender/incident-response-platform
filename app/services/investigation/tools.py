from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from sqlmodel import Session, select

from app.models.telemetry import TelemetryLog, TelemetryMetric, LogLevel
from app.models.deployment import Deployment
from app.models.service import Service
from app.models.knowledge import Runbook, PastIncident


def query_logs(
    session: Session,
    service: str,
    level: Optional[str] = None,
    search_query: Optional[str] = None,
    time_window_minutes: int = 30,
    limit: int = 25,
) -> Dict[str, Any]:
    """Queries application logs for a given service within a time window."""
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(minutes=time_window_minutes)

    query = select(TelemetryLog).where(
        TelemetryLog.service == service,
        TelemetryLog.timestamp >= window_start,
    )

    if level:
        query = query.where(TelemetryLog.level == level.upper())

    logs = session.exec(query.order_by(TelemetryLog.timestamp.desc()).limit(limit)).all()

    if search_query:
        query_lower = search_query.lower()
        logs = [l for l in logs if query_lower in l.message.lower()]

    return {
        "service": service,
        "count": len(logs),
        "logs": [
            {
                "id": l.id,
                "timestamp": l.timestamp.isoformat(),
                "level": l.level,
                "message": l.message,
                "trace_id": l.trace_id,
                "metadata": l.metadata_json,
            }
            for l in logs
        ],
    }


def query_metrics(
    session: Session,
    service: str,
    metric_names: Optional[List[str]] = None,
    time_window_minutes: int = 30,
) -> Dict[str, Any]:
    """Queries time-series telemetry metrics for a service."""
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(minutes=time_window_minutes)

    query = select(TelemetryMetric).where(
        TelemetryMetric.service == service,
        TelemetryMetric.timestamp >= window_start,
    )

    metrics = session.exec(query.order_by(TelemetryMetric.timestamp.asc())).all()

    if metric_names:
        metrics = [m for m in metrics if m.metric_name in metric_names]

    # Summarize stats per metric
    summary: Dict[str, Dict[str, Any]] = {}
    for m in metrics:
        if m.metric_name not in summary:
            summary[m.metric_name] = {"latest": m.value, "max": m.value, "min": m.value, "unit": m.unit, "count": 0}
        summary[m.metric_name]["latest"] = m.value
        summary[m.metric_name]["max"] = max(summary[m.metric_name]["max"], m.value)
        summary[m.metric_name]["min"] = min(summary[m.metric_name]["min"], m.value)
        summary[m.metric_name]["count"] += 1

    return {
        "service": service,
        "metrics_summary": summary,
        "raw_points_count": len(metrics),
    }


def get_recent_deployments(
    session: Session,
    service: str,
    limit: int = 5,
) -> Dict[str, Any]:
    """Retrieves recent deployment history and changes for a service."""
    deployments = session.exec(
        select(Deployment)
        .where(Deployment.service == service)
        .order_by(Deployment.timestamp.desc())
        .limit(limit)
    ).all()

    return {
        "service": service,
        "count": len(deployments),
        "deployments": [
            {
                "id": d.id,
                "version": d.version,
                "commit_hash": d.commit_hash,
                "deployed_by": d.deployed_by,
                "status": d.status,
                "timestamp": d.timestamp.isoformat(),
                "changes_summary": d.changes_summary,
                "rollback_version": d.rollback_version,
            }
            for d in deployments
        ],
    }


def get_service_dependencies(
    session: Session,
    service_name: str,
) -> Dict[str, Any]:
    """Retrieves service dependency graph and current health status of upstream/downstream services."""
    service = session.exec(select(Service).where(Service.name == service_name)).first()
    if not service:
        return {"error": f"Service {service_name} not found"}

    dep_status = []
    for dep_name in service.dependencies:
        dep_srv = session.exec(select(Service).where(Service.name == dep_name)).first()
        dep_status.append({
            "name": dep_name,
            "status": dep_srv.status if dep_srv else "unknown",
            "version": dep_srv.current_version if dep_srv else "unknown",
        })

    return {
        "service": service.name,
        "status": service.status,
        "current_version": service.current_version,
        "dependencies": dep_status,
    }


def inspect_database_health(
    session: Session,
    service_name: str = "postgres-db",
) -> Dict[str, Any]:
    """Inspects database metrics, connection pools, and lock health."""
    db_metrics = session.exec(
        select(TelemetryMetric).where(TelemetryMetric.service == "postgres-db")
    ).all()

    latest_active_conn = 25.0
    for m in db_metrics:
        if m.metric_name == "active_connections":
            latest_active_conn = m.value

    return {
        "database": "PostgreSQL 16.2",
        "active_connections": latest_active_conn,
        "max_connections_limit": 100,
        "connection_pool_health": "CRITICAL" if latest_active_conn >= 90 else "HEALTHY",
        "lock_contention": "LOW",
        "disk_usage_percent": 34.2,
    }
