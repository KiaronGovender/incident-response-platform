# Autonomous Production Incident Response Platform

## Project Specification

**Project status:** In development
**Target:** Production-grade portfolio project
**Primary stack:** Python, FastAPI, PostgreSQL, Redis, Docker, Google Cloud, GitHub Actions, LangGraph, LLMs
**Deployment:** Google Cloud Run
**Repository:** `KiaronGovender/incident-response-platform`

---

# 1. Project Overview

The Autonomous Production Incident Response Platform is an AI-powered system designed to detect, investigate, explain, and assist with the resolution of production software incidents.

The system simulates the type of tooling used by modern engineering and DevOps teams when production systems experience failures.

Instead of simply displaying alerts, the platform should be capable of taking an incident and autonomously investigating it by collecting evidence from multiple sources, forming hypotheses, testing those hypotheses using available tools, identifying the most likely root cause, and producing an explanation and recommended remediation.

The long-term goal is to create a system that demonstrates practical software engineering, cloud engineering, DevOps, distributed systems, observability, databases, AI agents, RAG, and production deployment.

The project must remain an **engineering system first and an AI system second**.

The AI should interact with real application data and tools rather than simply generating plausible text.

---

# 2. Core Problem

Production incidents often require engineers to manually correlate information from multiple systems:

- Application logs
- Metrics
- Deployment history
- Database behaviour
- Infrastructure health
- Service dependencies
- Alerts
- Configuration changes
- Previous incidents
- Runbooks

For example:

```text
14:01  payment-api deployment
14:03  request latency increases
14:04  HTTP 500 rate increases
14:05  database connection pool exhausted
14:06  monitoring creates alert
14:07  engineer begins investigation
```

A human engineer must determine whether these events are related.

The platform should eventually be able to perform much of this investigation automatically.

---

# 3. Primary Objective

Given a production incident, the platform should be capable of:

```text
Detect
   ↓
Create Incident
   ↓
Collect Evidence
   ↓
Analyse Evidence
   ↓
Form Hypotheses
   ↓
Use Investigation Tools
   ↓
Test Hypotheses
   ↓
Determine Likely Root Cause
   ↓
Generate Incident Summary
   ↓
Recommend Remediation
   ↓
Optionally Execute Approved Remediation
```

The system must maintain a clear record of how it reached its conclusion.

---

# 4. What the Finished System Should Demonstrate

The completed project should demonstrate competence in:

### Backend Engineering

- Python
- FastAPI
- REST APIs
- Pydantic
- SQLModel / SQLAlchemy
- PostgreSQL
- Database relationships
- Transactions
- Background processing
- API validation
- Error handling
- Authentication/authorization where appropriate

### Cloud Engineering

- Google Cloud
- Cloud Run
- Cloud SQL
- Artifact Registry
- IAM
- Workload Identity Federation
- Cloud logging/monitoring
- Environment configuration
- Secret management

### DevOps

- Docker
- GitHub Actions
- CI/CD
- Automated testing
- Immutable container versions
- Deployment automation
- Infrastructure-aware application design
- Health checks
- Rollbacks

### Distributed Systems

- Redis
- Queues
- Background workers
- Asynchronous processing
- Idempotency
- Retry handling
- Failure recovery

### Observability

- Structured logging
- Metrics
- Health checks
- Incident timelines
- Error rates
- Latency
- Service dependencies
- Deployment tracking

### AI Engineering

- LLM integration
- Tool calling
- Agent workflows
- LangGraph
- RAG
- Embeddings
- Vector search
- Structured outputs
- Agent state
- Evidence-based reasoning
- Human approval workflows

---

# 5. System Architecture

The target architecture is:

```text
                         ┌─────────────────────┐
                         │    Web Dashboard    │
                         │    React / Next.js  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      FastAPI        │
                         │        API          │
                         └──────────┬──────────┘
                                    │
                  ┌─────────────────┼─────────────────┐
                  │                 │                 │
                  ▼                 ▼                 ▼
             Incident API      Telemetry API     Investigation API
                  │                 │                 │
                  └─────────────────┼─────────────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     PostgreSQL      │
                         │                     │
                         │ Incidents           │
                         │ Events              │
                         │ Services            │
                         │ Deployments          │
                         │ Investigations       │
                         │ Findings             │
                         └──────────┬──────────┘
                                    │
                                    ▼
                              ┌───────────┐
                              │   Redis   │
                              │   Queue   │
                              └─────┬─────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Background Workers  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   AI Investigation  │
                         │       Agent          │
                         │                     │
                         │     LangGraph       │
                         └──────────┬──────────┘
                                    │
                 ┌──────────────────┼──────────────────┐
                 ▼                  ▼                  ▼
             Log Tool          Metrics Tool      Deployment Tool
                 │                  │                  │
                 └──────────────────┼──────────────────┘
                                    │
                                    ▼
                              ┌───────────┐
                              │    RAG    │
                              │           │
                              │ Runbooks  │
                              │ Previous  │
                              │ Incidents │
                              └───────────┘
```

---

# 6. Core Domain Model

The system should eventually contain the following major entities.

## Incident

Represents a production incident.

An incident should contain:

- ID
- Title
- Description
- Affected service
- Severity
- Status
- Creation time
- Detection time
- Resolution time
- Current investigation state
- Root cause
- Resolution summary

Example:

```json
{
  "id": "inc_123",
  "title": "Payment API elevated error rate",
  "service": "payment-api",
  "severity": "high",
  "status": "investigating"
}
```

---

# 7. Incident Events

An incident consists of evidence collected over time.

Supported event categories should include:

```text
LOG
METRIC
ALERT
DEPLOYMENT
INFRASTRUCTURE
CONFIGURATION
DATABASE
SERVICE_HEALTH
```

Example:

```json
{
  "event_type": "deployment",
  "source": "github-actions",
  "message": "payment-api v2.4.1 deployed",
  "timestamp": "2026-08-28T09:25:00"
}
```

Events must be associated with an incident.

The system must preserve the chronological incident timeline.

---

# 8. Services

The platform should understand that incidents affect services.

A service should contain information such as:

- Name
- Environment
- Owner
- Repository
- Current version
- Dependencies
- Health status

Example:

```text
payment-api
    │
    ├── PostgreSQL
    ├── Redis
    └── authentication-service
```

This dependency information will eventually allow the AI agent to investigate upstream and downstream failures.

---

# 9. Telemetry

The platform should eventually receive or simulate production telemetry.

Telemetry should include:

### Logs

```text
INFO
WARN
ERROR
CRITICAL
```

### Metrics

Examples:

```text
request_count
error_rate
request_latency
cpu_usage
memory_usage
database_latency
connection_pool_usage
```

### Deployments

Examples:

```text
version
commit
timestamp
environment
deployment_status
```

### Alerts

Examples:

```text
error rate > threshold
latency > threshold
service unavailable
database connections exhausted
```

---

# 10. Incident Detection

The system should eventually be capable of detecting abnormal behaviour.

Example:

```text
Normal error rate: 0.5–2%

Current error rate: 18.7%

        ↓

Threshold exceeded

        ↓

Create incident
```

Detection does not need to use machine learning initially.

Rule-based detection is acceptable and preferred for the first implementation.

Later, anomaly detection can be introduced.

---

# 11. Investigation Engine

The investigation engine is the core of the project.

When an incident enters the investigation state:

```text
Incident
   ↓
Investigation started
```

the system should gather relevant evidence.

The investigation should produce:

```text
Evidence
Hypotheses
Tool Calls
Findings
Root Cause
Confidence
Recommendations
```

---

# 12. AI Agent

The AI agent must not simply receive:

> "The payment service is broken."

and generate an answer.

Instead, the agent should have access to tools.

Example:

```text
Incident
    ↓
Agent
    │
    ├── query_logs()
    │
    ├── query_metrics()
    │
    ├── get_recent_deployments()
    │
    ├── get_service_dependencies()
    │
    ├── search_runbooks()
    │
    └── search_previous_incidents()
```

The agent should use evidence from those tools to investigate the incident.

---

# 13. Investigation Loop

The target investigation loop is:

```text
┌──────────────────────┐
│   Receive Incident   │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Gather Initial Data  │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Form Hypotheses      │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Select Investigation │
│ Tool                 │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Gather Evidence      │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ Evaluate Evidence    │
└──────────┬───────────┘
           ↓
      More evidence?
       /          \
     YES           NO
      │             │
      └──────┐      ↓
             │   Root Cause
             │      │
             └──────┘
                    ↓
             Recommendation
```

The agent should be able to revise its hypothesis when evidence contradicts it.

---

# 14. Evidence-Based Reasoning

The system must distinguish between:

### Evidence

Something directly observed.

Example:

```text
Error rate increased from 1.2% to 18.7%.
```

### Hypothesis

A possible explanation.

Example:

```text
The latest deployment may have introduced the failure.
```

### Finding

A conclusion supported by multiple pieces of evidence.

Example:

```text
The database connection pool became exhausted immediately
after deployment v2.4.1.
```

### Root Cause

The most likely underlying cause.

Example:

```text
Deployment v2.4.1 introduced a connection leak that caused
the PostgreSQL connection pool to become exhausted.
```

The system should avoid presenting speculation as fact.

---

# 15. RAG System

The platform should eventually contain a knowledge base containing:

- Runbooks
- Troubleshooting guides
- Previous incidents
- Architecture documentation
- Service documentation
- Known failure patterns

The agent should be able to search this information.

Example:

```text
Incident
   ↓
Agent
   ↓
Search knowledge base
   ↓
Relevant runbook
   ↓
Additional investigation
```

The RAG system should provide citations/references to the source documents used by the agent.

---

# 16. Autonomous Remediation

The final system may support controlled remediation.

Examples:

```text
Restart service
Rollback deployment
Scale service
Clear unhealthy worker
Disable problematic feature flag
```

However, the system must **not automatically execute destructive actions by default**.

The preferred model is:

```text
AI identifies remediation
        ↓
Risk assessment
        ↓
Human approval
        ↓
Execute
        ↓
Verify result
```

For low-risk actions, automated execution may eventually be supported.

---

# 17. Remediation Verification

After remediation, the system should verify whether the incident improved.

Example:

```text
Before:
Error rate = 18.7%

        ↓

Rollback deployment

        ↓

After:
Error rate = 1.1%

        ↓

Incident resolved
```

The platform should record the remediation and its outcome.

---

# 18. Incident Timeline

Every investigation should produce a timeline.

Example:

```text
09:25:00  Deployment v2.4.1
09:30:12  Error rate exceeds threshold
09:30:15  Incident created
09:31:03  Agent queries application logs
09:31:07  Database connection errors discovered
09:31:15  Agent checks deployment history
09:31:20  Deployment identified as probable cause
09:32:01  Runbook retrieved
09:32:45  Rollback recommended
09:33:10  Human approves rollback
09:33:42  Rollback completed
09:34:10  Error rate returns to normal
09:34:15  Incident resolved
```

This timeline is a key feature of the platform.

---

# 19. AI Investigation State

The agent should maintain structured state.

Example:

```json
{
  "incident_id": "inc_123",
  "current_hypothesis": "database connection exhaustion",
  "confidence": 0.87,
  "evidence": [
    "connection pool exhausted",
    "error rate increased",
    "deployment occurred 5 minutes earlier"
  ],
  "tools_used": ["query_logs", "query_metrics", "get_recent_deployments"],
  "next_action": "search_runbooks"
}
```

This state should be persisted where appropriate so investigations can survive worker restarts.

---

# 20. Background Processing

Investigations should not block normal API requests.

The architecture should eventually be:

```text
POST /incidents
        ↓
Create incident
        ↓
Queue investigation job
        ↓
Return response
        ↓
Redis
        ↓
Worker
        ↓
AI investigation
```

The API should remain responsive while long-running investigations occur in the background.

---

# 21. Failure Handling

The system must be designed for failure.

Examples:

### LLM unavailable

The investigation should enter a retryable state.

### Database unavailable

The API should return an appropriate error and log the failure.

### Tool failure

The agent should record the failed tool call and attempt an alternative investigation path where possible.

### Worker crash

The job should be recoverable.

### Duplicate event

The system should avoid creating duplicate events where idempotency is required.

---

# 22. Security

Security is part of the project rather than an afterthought.

The system should eventually implement:

- Environment-based secrets
- No secrets committed to Git
- IAM
- Workload Identity Federation
- Least-privilege service accounts
- Authentication
- Authorization
- Input validation
- Secure API configuration
- Audit logging
- Controlled remediation permissions

AI-generated commands should never automatically receive unrestricted production access.

---

# 23. CI/CD

The project already has a working CI/CD foundation.

Current deployment flow:

```text
GitHub
   ↓
GitHub Actions
   ↓
Tests
   ↓
Docker Build
   ↓
Google Cloud Authentication
   ↓
Artifact Registry
   ↓
Cloud Run
```

Authentication uses:

```text
GitHub OIDC
       ↓
Google Cloud Workload Identity Federation
```

No long-lived Google Cloud service-account key should be stored in GitHub.

Future improvements may include:

- Linting
- Type checking
- Security scanning
- Container vulnerability scanning
- Deployment environments
- Automated rollback
- Preview environments

---

# 24. Cloud Architecture

The target Google Cloud architecture is:

```text
                    GitHub
                       │
                       ▼
                GitHub Actions
                       │
                       ▼
              Artifact Registry
                       │
                       ▼
                    Cloud Run
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
        FastAPI API          Workers
             │                   │
             └─────────┬─────────┘
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
         Cloud SQL             Redis
       PostgreSQL
             │
             ▼
       Incident Data
```

The exact Google Cloud services may evolve as the project grows.

---

# 25. Frontend

The platform should eventually include a dashboard.

The dashboard should display:

### Active incidents

```text
CRITICAL   Payment API
HIGH       Authentication Service
MEDIUM     Notification Service
```

### Incident detail

```text
Payment API Incident

Severity: HIGH
Status: INVESTIGATING

Error Rate
███████████████████

Timeline
09:25 Deployment
09:30 Error spike
09:31 DB errors
09:32 AI investigation
```

### AI Investigation

The UI should show:

```text
Current hypothesis:
Database connection exhaustion

Confidence:
87%

Evidence:
✓ Connection pool exhausted
✓ Error rate increased
✓ Deployment occurred 5 minutes earlier

Next action:
Searching deployment-related runbooks
```

The dashboard should make the AI's investigation observable rather than hiding it behind a chat interface.

---

# 26. Initial Simulated Production Environment

Because this is a portfolio project and we may not have access to a real production environment, the platform should include a simulated production environment.

It should contain multiple services.

Example:

```text
API Gateway
     │
     ├── Payment Service
     │       │
     │       └── PostgreSQL
     │
     ├── Authentication Service
     │
     └── Notification Service
```

The simulator should generate realistic telemetry.

---

# 27. Failure Scenarios

The simulator should eventually support deliberate failure scenarios.

Examples:

### Database connection exhaustion

```text
Database connections
████████████████████ 100%
```

### Deployment regression

```text
v2.4.0 → healthy
v2.4.1 → error rate spike
```

### Memory leak

```text
Memory
40% → 55% → 72% → 91% → crash
```

### Increased latency

```text
P95 latency
200ms → 400ms → 900ms → 2.4s
```

### Dependency failure

```text
Payment Service
      ↓
External Payment Provider
      ↓
Unavailable
```

The agent should eventually be capable of distinguishing these scenarios.

---

# 28. Testing Strategy

The project should eventually contain:

### Unit tests

Test individual components.

### API tests

Test FastAPI endpoints.

### Database tests

Test persistence and relationships.

### Agent tests

Test tool selection and investigation behaviour.

### Integration tests

Test:

```text
API → Database
API → Queue
Worker → AI
Worker → Tools
```

### End-to-end tests

Simulate:

```text
Failure
 ↓
Detection
 ↓
Incident
 ↓
Investigation
 ↓
Root cause
 ↓
Resolution
```

---

# 29. Observability

The platform itself should be observable.

It should eventually provide:

- Structured application logs
- Request IDs
- Incident IDs
- Investigation IDs
- Agent execution traces
- Tool execution logs
- Processing latency
- Queue depth
- Error rates
- AI token/cost metrics where available

Every major operation should be traceable back to an incident.

---

# 30. Non-Goals

This project is **not** intended to become:

- A generic ChatGPT clone
- A simple chatbot
- A static dashboard
- A collection of unrelated AI demos
- A toy CRUD application
- An autonomous system with unrestricted production access

The AI must solve a real engineering problem.

---

# 31. Development Philosophy

The project should be built incrementally.

We should avoid introducing technologies simply because they look impressive on a resume.

Each technology must solve a real problem.

For example:

```text
PostgreSQL
→ persistent incident state

Redis
→ asynchronous investigation jobs

LangGraph
→ stateful investigation workflow

RAG
→ access to operational knowledge

Cloud Run
→ scalable container deployment

GitHub Actions
→ automated delivery
```

If a technology does not have a clear architectural purpose, it should not be added.

---

# 32. Development Phases

## Phase 1 — Foundation

Completed.

- FastAPI
- Project structure
- Health endpoint
- Tests
- Docker
- Google Cloud
- Artifact Registry
- Cloud Run
- GitHub Actions
- Workload Identity Federation
- Automated deployment

---

## Phase 2 — Incident Management

Current.

- Incident model
- Incident API
- Event model
- Event API
- Incident timeline

---

## Phase 3 — Persistent Data

Current/next.

- PostgreSQL
- SQLModel
- Database relationships
- Alembic
- Database migrations
- Indexing
- Transactions

---

## Phase 4 — Production Simulator

Build:

- Multiple services
- Logs
- Metrics
- Deployments
- Alerts
- Service dependencies
- Failure injection

---

## Phase 5 — Incident Detection

Build:

- Threshold detection
- Alert processing
- Automatic incident creation
- Severity calculation
- Incident state transitions

---

## Phase 6 — Investigation Engine

Build:

- Investigation jobs
- Redis
- Background workers
- Investigation state
- Evidence collection
- Hypotheses
- Findings

---

## Phase 7 — AI Agent

Build:

- LLM integration
- Tool calling
- LangGraph
- Stateful agent workflow
- Investigation loop
- Structured outputs
- Confidence scoring

---

## Phase 8 — RAG

Build:

- Operational knowledge base
- Document ingestion
- Chunking
- Embeddings
- Vector search
- Runbook retrieval
- Previous incident retrieval
- Source attribution

---

## Phase 9 — Remediation

Build:

- Remediation recommendations
- Risk classification
- Human approval
- Controlled tool execution
- Rollback simulation
- Remediation verification

---

## Phase 10 — Dashboard

Build:

- Incident dashboard
- Incident detail
- Timeline
- AI investigation view
- Evidence explorer
- Root cause display
- Remediation interface

---

## Phase 11 — Production Hardening

Improve:

- Authentication
- Authorization
- Security
- Observability
- Metrics
- Tracing
- Error handling
- Retry logic
- Idempotency
- Rate limiting
- CI/CD security
- Container scanning
- Cost controls

---

# 33. Definition of Done

The project is considered complete when a user can:

1. Start the simulated production environment.
2. Inject a realistic failure.
3. Have the system detect the abnormal behaviour.
4. Automatically create an incident.
5. Collect relevant telemetry.
6. Start an asynchronous investigation.
7. Have the AI agent use investigation tools.
8. Search operational knowledge using RAG.
9. Form and evaluate multiple hypotheses.
10. Identify the most likely root cause.
11. Explain the reasoning using actual evidence.
12. Recommend a remediation.
13. Require human approval for risky remediation.
14. Execute the approved remediation.
15. Verify whether the remediation worked.
16. Resolve the incident.
17. Display the complete incident timeline.
18. Persist all important investigation information.
19. Run the entire platform through automated CI/CD.
20. Deploy the production application to Google Cloud.

---

# 34. Portfolio Goal

The project should communicate the following to a technical recruiter:

> This developer can build more than CRUD applications.

It should demonstrate that the developer understands how modern production systems are built and operated.

The project should show:

```text
Software Engineering
        +
Cloud Engineering
        +
DevOps
        +
Distributed Systems
        +
Observability
        +
AI Engineering
```

The AI component should be integrated into a genuine engineering workflow rather than added merely as a feature.

---

# 35. Resume-Level Description

When completed, the project should be capable of being described approximately as:

> **Autonomous Production Incident Response Platform** — Built and deployed a cloud-native incident response platform that automatically detects simulated production failures, correlates logs, metrics and deployment events, and uses a stateful AI agent with tool calling and RAG to investigate incidents, identify probable root causes, and recommend controlled remediation. Implemented asynchronous investigation workers, PostgreSQL persistence, Redis-based job processing, Dockerized services, GitHub Actions CI/CD, and Google Cloud deployment.

This description should only be used once the corresponding functionality actually exists.

---

# 36. Guiding Principle

The most important principle for the entire project is:

> **The agent must investigate the system, not simply talk about the system.**

Every major AI capability should therefore answer:

```text
What data did the agent access?
What tool did it use?
What evidence did it find?
What hypothesis did it form?
Why did the evidence support or reject that hypothesis?
What action did it take next?
```

If we maintain this principle, the project will remain an engineering-focused autonomous incident response platform rather than becoming another generic AI chatbot.
