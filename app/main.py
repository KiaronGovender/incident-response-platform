import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.db.init_db import init_db
from app.routes.incidents import router as incidents_router
from app.routes.events import router as events_router
from app.routes.investigations import router as investigations_router
from app.routes.services import router as services_router
from app.routes.telemetry import router as telemetry_router
from app.routes.simulator import router as simulator_router
from app.routes.remediations import router as remediations_router
from app.routes.knowledge import router as knowledge_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Autonomous Incident Response Platform",
    description="Autonomous production incident detection, SRE investigation agent, and remediation platform.",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for Next.js dashboard & dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "system": "Autonomous Production Incident Response Platform",
        "version": "1.0.0",
        "ai_engine": "Autonomous Multi-Step Agent Active",
    }


# Include API Routers
app.include_router(incidents_router)
app.include_router(events_router)
app.include_router(investigations_router)
app.include_router(services_router)
app.include_router(telemetry_router)
app.include_router(simulator_router)
app.include_router(remediations_router)
app.include_router(knowledge_router)

# Mount Next.js static export if present (for production Cloud Run single container deployment)
frontend_out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "out")
if os.path.exists(frontend_out):
    app.mount("/", StaticFiles(directory=frontend_out, html=True), name="frontend")