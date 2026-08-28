from sqlmodel import SQLModel, Session, select, text
from app.db.database import engine
from app.models import (
    Incident,
    IncidentEvent,
    Investigation,
    InvestigationHypothesis,
    InvestigationToolCall,
    Service,
    ServiceStatus,
    Deployment,
    DeploymentStatus,
    TelemetryMetric,
    TelemetryLog,
    RemediationAction,
    Runbook,
    PastIncident,
)
from datetime import datetime, timezone, timedelta


def migrate_tables():
    """Ensures newly added columns and enum type conversions in existing Postgres database."""
    dialect = engine.dialect.name
    if dialect == "postgresql":
        with engine.connect() as conn:
            # Add any missing columns to existing incident table
            conn.execute(text("ALTER TABLE incident ADD COLUMN IF NOT EXISTS root_cause VARCHAR;"))
            conn.execute(text("ALTER TABLE incident ADD COLUMN IF NOT EXISTS resolution_summary VARCHAR;"))
            conn.execute(text("ALTER TABLE incident ADD COLUMN IF NOT EXISTS confidence_score FLOAT;"))
            conn.execute(text("ALTER TABLE incident ADD COLUMN IF NOT EXISTS detection_time TIMESTAMP WITHOUT TIME ZONE;"))
            conn.execute(text("ALTER TABLE incident ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMP WITHOUT TIME ZONE;"))
            conn.execute(text("ALTER TABLE incident ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITHOUT TIME ZONE;"))

            # Convert enum columns to VARCHAR so all values are accepted seamlessly
            conn.execute(text("ALTER TABLE incident ALTER COLUMN status TYPE VARCHAR USING status::VARCHAR;"))
            conn.execute(text("ALTER TABLE incident ALTER COLUMN severity TYPE VARCHAR USING severity::VARCHAR;"))
            conn.execute(text("ALTER TABLE incidentevent ALTER COLUMN event_type TYPE VARCHAR USING event_type::VARCHAR;"))
            conn.commit()


def seed_initial_data():
    with Session(engine) as session:
        # Check if services already seeded
        existing_services = session.exec(select(Service)).first()
        if not existing_services:
            services = [
                Service(
                    id="srv_api_gateway",
                    name="api-gateway",
                    environment="production",
                    owner="edge-team",
                    repository="KiaronGovender/incident-response-platform",
                    current_version="v3.1.0",
                    status=ServiceStatus.HEALTHY,
                    dependencies=["auth-service", "payment-api", "order-service"],
                    health_check_url="http://api-gateway/health",
                ),
                Service(
                    id="srv_payment_api",
                    name="payment-api",
                    environment="production",
                    owner="payments-team",
                    repository="KiaronGovender/incident-response-platform",
                    current_version="v2.4.1",
                    status=ServiceStatus.HEALTHY,
                    dependencies=["postgres-db", "redis-cache", "external-payment-gateway"],
                    health_check_url="http://payment-api/health",
                ),
                Service(
                    id="srv_auth_service",
                    name="auth-service",
                    environment="production",
                    owner="security-team",
                    repository="KiaronGovender/incident-response-platform",
                    current_version="v1.8.2",
                    status=ServiceStatus.HEALTHY,
                    dependencies=["postgres-db", "redis-cache"],
                    health_check_url="http://auth-service/health",
                ),
                Service(
                    id="srv_order_service",
                    name="order-service",
                    environment="production",
                    owner="core-team",
                    repository="KiaronGovender/incident-response-platform",
                    current_version="v2.0.4",
                    status=ServiceStatus.HEALTHY,
                    dependencies=["postgres-db", "notification-service"],
                    health_check_url="http://order-service/health",
                ),
                Service(
                    id="srv_notification_service",
                    name="notification-service",
                    environment="production",
                    owner="comms-team",
                    repository="KiaronGovender/incident-response-platform",
                    current_version="v1.4.0",
                    status=ServiceStatus.HEALTHY,
                    dependencies=["redis-cache"],
                    health_check_url="http://notification-service/health",
                ),
                Service(
                    id="srv_postgres_db",
                    name="postgres-db",
                    environment="production",
                    owner="database-infra",
                    repository="KiaronGovender/incident-response-platform",
                    current_version="PostgreSQL 16.2",
                    status=ServiceStatus.HEALTHY,
                    dependencies=[],
                    health_check_url="http://postgres-db:5432",
                ),
                Service(
                    id="srv_redis_cache",
                    name="redis-cache",
                    environment="production",
                    owner="cache-infra",
                    repository="KiaronGovender/incident-response-platform",
                    current_version="Redis 7.2",
                    status=ServiceStatus.HEALTHY,
                    dependencies=[],
                    health_check_url="http://redis-cache:6379",
                ),
            ]
            for s in services:
                session.add(s)

        # Check if Runbooks seeded
        existing_runbooks = session.exec(select(Runbook)).first()
        if not existing_runbooks:
            runbooks = [
                Runbook(
                    id="rb_001",
                    title="Database Connection Pool Saturation Remediation",
                    service="payment-api",
                    trigger_patterns=[
                        "connection pool exhausted",
                        "QueuePool limit of size",
                        "TimeoutError: could not obtain connection",
                        "500 Internal Server Error spikes after deployment",
                    ],
                    diagnosis_steps=[
                        "Inspect recent deployment logs for unclosed DB sessions",
                        "Check active Postgres connections via pg_stat_activity",
                        "Verify pool size configuration (max_overflow, pool_size)",
                        "Check if transaction leak correlates with newly introduced endpoints",
                    ],
                    remediation_actions=[
                        "Roll back recent application deployment to previous known healthy version",
                        "Restart application pods to clear hung connections",
                        "Temporarily scale DB connection pool max_overflow if traffic surge",
                    ],
                    risk_level="medium",
                    content="""# Runbook: DB Connection Pool Exhaustion
### Symptoms
- Sudden HTTP 500 error rate elevation (15-40%)
- Latency P95 increases from ~80ms to >3000ms
- Logs show `QueuePool limit of size 20 overflow 10 reached`

### Root Cause Patterns
1. Code deployment missing `session.close()` or missing context manager in new endpoint.
2. Long-running queries blocking worker threads.

### Safe Mitigation
1. Identify recently deployed version via deployment history.
2. Execute automated rollback to previous version.
3. Restart pods in rolling sequence.""",
                    tags=["database", "connections", "rollback", "sqlalchemy", "pool"],
                ),
                Runbook(
                    id="rb_002",
                    title="Deployment Regression Rollback & Recovery",
                    service="general",
                    trigger_patterns=[
                        "deployment regression",
                        "error rate spike immediately following deployment",
                        "NullPointerException",
                        "AttributeError",
                    ],
                    diagnosis_steps=[
                        "Check timestamp of last deployment against alert trigger time",
                        "Examine stack traces in application logs for newly introduced errors",
                        "Compare git commit diff between current and previous release",
                    ],
                    remediation_actions=[
                        "Execute instantaneous deployment rollback to last stable version",
                        "Validate error rate drops below 1% within 2 minutes of rollback",
                    ],
                    risk_level="medium",
                    content="""# Runbook: Deployment Regression Rollback
### Description
When a newly deployed container version introduces crashes or unhandled exceptions, immediate rollback is prioritized over debugging in production.

### Action Plan
1. Retrieve previous successful version tag from deployment registry.
2. Issue rollback deployment command.
3. Observe health metrics for 120 seconds.""",
                    tags=["deployment", "rollback", "regression", "release"],
                ),
                Runbook(
                    id="rb_003",
                    title="Downstream External Gateway Outage & Circuit Breaking",
                    service="payment-api",
                    trigger_patterns=[
                        "external payment provider",
                        "503 Service Unavailable",
                        "gateway timeout",
                        "Connection refused: api.stripe.com",
                    ],
                    diagnosis_steps=[
                        "Verify external vendor status page and DNS resolution",
                        "Check upstream egress HTTP error codes vs internal database health",
                    ],
                    remediation_actions=[
                        "Enable secondary payment processor fallback route",
                        "Enable circuit breaker to fast-fail pending checkout requests",
                    ],
                    risk_level="low",
                    content="""# Runbook: External Gateway Outage
### Mitigation
Activate the payment provider fallback route or switch circuit breaker to OPEN state.""",
                    tags=["external", "gateway", "third-party", "circuit-breaker"],
                ),
                Runbook(
                    id="rb_004",
                    title="Memory Leak & OOM Recovery Runbook",
                    service="order-service",
                    trigger_patterns=[
                        "memory usage > 90%",
                        "OOMKilled",
                        "java.lang.OutOfMemoryError",
                        "MemoryLimitExceeded",
                    ],
                    diagnosis_steps=[
                        "Check memory trend over past 60 minutes",
                        "Identify worker queues buffering messages without consumer ack",
                    ],
                    remediation_actions=[
                        "Restart failing pods with rolling strategy",
                        "Scale horizontal pod replicas to distribute memory load",
                        "Purge non-critical message buffer",
                    ],
                    risk_level="low",
                    content="""# Runbook: Memory Saturation & OOM
### Immediate Remediation
Restart service container to release leaked memory buffers while engineering patch is prepared.""",
                    tags=["memory", "oom", "scaling", "restart"],
                ),
            ]
            for rb in runbooks:
                session.add(rb)

        # Check if Past Incidents seeded
        existing_past = session.exec(select(PastIncident)).first()
        if not existing_past:
            past_incidents = [
                PastIncident(
                    id="inc_past_001",
                    title="Payment API DB Connection Exhaustion Post-Deployment",
                    service="payment-api",
                    root_cause="Commit 8f3b12a introduced an unmanaged database session inside the async webhook listener, preventing connection release under concurrent traffic.",
                    resolution="Rolled back payment-api from v2.3.0 to v2.2.9. Applied context manager fix in v2.3.1.",
                    symptoms=[
                        "Error rate spiked to 24%",
                        "Database connection pool 100% full",
                        "Timeout acquiring DB connection",
                    ],
                    postmortem_url="https://wiki.internal/postmortems/2025-08-12-payment-db-pool",
                ),
                PastIncident(
                    id="inc_past_002",
                    title="Auth Service Token Validation CrashLoop",
                    service="auth-service",
                    root_cause="v1.8.0 release contained unhandled null check when JWT claims omitted optional aud field.",
                    resolution="Rolled back auth-service to v1.7.9. Added schema validation unit test.",
                    symptoms=[
                        "Auth error rate 50%",
                        "NullPointerException in TokenValidator.java",
                        "500 Internal Server Error on /auth/verify",
                    ],
                    postmortem_url="https://wiki.internal/postmortems/2025-11-04-auth-token-crash",
                ),
            ]
            for pi in past_incidents:
                session.add(pi)

        # Seed initial deployments
        existing_deployments = session.exec(select(Deployment)).first()
        if not existing_deployments:
            now = datetime.now(timezone.utc)
            deployments = [
                Deployment(
                    id="dep_001",
                    service="payment-api",
                    version="v2.4.0",
                    commit_hash="a1b2c3d",
                    deployed_by="github-actions",
                    status=DeploymentStatus.SUCCESSFUL,
                    timestamp=now - timedelta(hours=24),
                    changes_summary="Optimized payment gateway retry backoff",
                ),
                Deployment(
                    id="dep_002",
                    service="payment-api",
                    version="v2.4.1",
                    commit_hash="e4f5g6h",
                    deployed_by="github-actions",
                    status=DeploymentStatus.SUCCESSFUL,
                    timestamp=now - timedelta(minutes=15),
                    changes_summary="Refactored database query execution pipeline",
                    rollback_version="v2.4.0",
                ),
                Deployment(
                    id="dep_003",
                    service="auth-service",
                    version="v1.8.2",
                    commit_hash="f7g8h9i",
                    deployed_by="github-actions",
                    status=DeploymentStatus.SUCCESSFUL,
                    timestamp=now - timedelta(days=2),
                    changes_summary="Upgraded token encryption cipher suite",
                ),
                Deployment(
                    id="dep_004",
                    service="order-service",
                    version="v2.0.4",
                    commit_hash="j1k2l3m",
                    deployed_by="github-actions",
                    status=DeploymentStatus.SUCCESSFUL,
                    timestamp=now - timedelta(hours=6),
                    changes_summary="Added batch order status polling",
                ),
            ]
            for dep in deployments:
                session.add(dep)

        session.commit()


def init_db():
    SQLModel.metadata.create_all(engine)
    migrate_tables()
    seed_initial_data()