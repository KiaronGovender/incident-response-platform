# Autonomous Production Incident Response Platform

An autonomous, AI-driven production incident detection, investigation, and controlled remediation platform designed to simulate modern site reliability engineering (SRE) workflows.

The system correlates real-time logs, metrics, service topology, and deployment histories, uses autonomous multi-step agent reasoning with diagnostic tools and RAG knowledge retrieval, formulates competing hypotheses with confidence scoring, and executes controlled, human-approved remediations.

---

## Architecture Overview

```text
                           ┌────────────────────────────┐
                           │    Next.js Web Cockpit     │
                           │   (React / Tailwind CSS)   │
                           └─────────────┬──────────────┘
                                         │ HTTP / REST
                                         ▼
                           ┌────────────────────────────┐
                           │      FastAPI Backend       │
                           │        (Port 8000)         │
                           └─────────────┬──────────────┘
                                         │
       ┌──────────────────┬──────────────┼──────────────┬──────────────────┐
       │                  │              │              │                  │
       ▼                  ▼              ▼              ▼                  ▼
┌──────────────┐   ┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐
│ Incident API │   │Telemetry API ││Simulator Lab ││RAG Knowledge ││ Remediation  │
└──────┬───────┘   └──────┬───────┘└──────┬───────┘└──────┬───────┘└──────┬───────┘
       │                  │              │              │                 │
       └──────────────────┴──────────────┼──────────────┴─────────────────┘
                                         │
                                         ▼
                           ┌────────────────────────────┐
                           │   PostgreSQL / SQLModel    │
                           └─────────────┬──────────────┘
                                         │
                                         ▼
                           ┌────────────────────────────┐
                           │  Autonomous AI SRE Agent   │
                           │  (Evidence Reasoner / RAG) │
                           └─────────────┬──────────────┘
                                         │
                  ┌──────────────────────┼──────────────────────┐
                  ▼                      ▼                      ▼
           Log / Metric Tools     Deployment Tools       Runbook Citations
```

---

## Features

- **Automated Anomaly & SLA Detection:** Automatically detects threshold violations across error rates, P99 latency spikes, connection pool saturations, and memory leaks.
- **Autonomous Multi-Step AI Agent:**
  - Evaluates telemetry data without hallucinations by executing actual diagnostic tools (`query_metrics`, `query_logs`, `get_recent_deployments`, `inspect_database_health`).
  - Formulates and ranks competing hypotheses (`CONFIRMED` vs `REFUTED`) with mathematical evidence-based confidence scoring.
  - Retrieves authoritative operational runbooks and historical postmortems via RAG.
- **Controlled Human-in-the-Loop Remediation:**
  - Risk-classified mitigation actions (`LOW`, `MEDIUM`, `HIGH`).
  - Instantaneous rollback deployment, pod restarts, and circuit breaker failovers.
  - Automated post-remediation SLA verification and postmortem reporting.
- **Production Failure Simulator Lab:**
  - Inject 5+ real-world failure scenarios (Database Connection Pool Saturation, Out-Of-Memory CrashLoop, Token Parser Regression, External Gateway 503 Outage, Notification Queue Cascade).
- **Next.js Real-time Dashboard:**
  - Incident Control Center & Live Hypothesis Graph
  - Diagnostic Tool Execution Traces
  - Unified Chronological Timeline
  - Observability & Fleet Topology Map
  - Interactive RAG Knowledge Search

---

## Getting Started

### 1. Backend (FastAPI)

```powershell
# Activate Python virtual environment
.\.venv\Scripts\Activate.ps1

# Run automated test suite
pytest -v

# Start FastAPI development server
uvicorn app.main:app --reload --port 8000
```

FastAPI Swagger API docs will be available at: `http://localhost:8000/docs`

### 2. Frontend (Next.js Dashboard)

```powershell
cd frontend

# Run Next.js development server
npm.cmd run dev
```

Open `http://localhost:3000` in your browser to access the SRE Incident Response Cockpit.

---

## Automated Test Suite

Run the full pytest suite covering all 10 unit, API, agent, and End-to-End integration tests:

```powershell
pytest -v
```

Tests verified:
- `test_health.py`
- `test_incidents_api.py`
- `test_events_api.py`
- `test_simulator.py`
- `test_detection_engine.py`
- `test_investigation_tools.py`
- `test_rag_knowledge.py`
- `test_ai_agent_investigation.py`
- `test_remediation_workflow.py`
- `test_end_to_end_pipeline.py`
