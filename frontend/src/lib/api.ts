import {
  Incident,
  IncidentEvent,
  InvestigationDetail,
  Service,
  TelemetryMetric,
  TelemetryLog,
  RemediationAction,
  FailureScenario,
  Runbook,
  PastIncident,
  TimelineItem,
} from "./types";

const getApiBase = () => {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  if (typeof window !== "undefined") {
    if (window.location.port !== "3000") {
      return "";
    }
  }
  return "http://localhost:8000";
};

async function fetchJson<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${getApiBase()}${endpoint}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`API Error [${res.status} ${res.statusText}]: ${errorText}`);
  }

  return res.json() as Promise<T>;
}

export const api = {
  // Health
  getHealth: () => fetchJson<{ status: string; version: string; ai_engine: string }>("/health"),

  // Incidents
  getIncidents: (params?: { status?: string; severity?: string; service?: string }) => {
    const query = new URLSearchParams(params as Record<string, string>).toString();
    return fetchJson<Incident[]>(`/incidents/${query ? `?${query}` : ""}`);
  },

  getIncident: (id: string) => fetchJson<Incident>(`/incidents/${id}`),

  getIncidentTimeline: (id: string) =>
    fetchJson<{ incident_id: string; incident_title: string; status: string; timeline: TimelineItem[] }>(
      `/incidents/${id}/timeline`
    ),

  triggerInvestigation: (incidentId: string) =>
    fetchJson<any>(`/incidents/${incidentId}/investigate`, { method: "POST" }),

  // Events
  getIncidentEvents: (incidentId: string) =>
    fetchJson<IncidentEvent[]>(`/incidents/${incidentId}/events/`),

  // Investigations
  getInvestigationByIncident: (incidentId: string) =>
    fetchJson<InvestigationDetail | null>(`/investigations/incident/${incidentId}`),

  getInvestigationDetail: (investigationId: string) =>
    fetchJson<InvestigationDetail>(`/investigations/${investigationId}`),

  // Services
  getServices: () => fetchJson<Service[]>("/services/"),

  // Telemetry
  getMetrics: (params?: { service?: string; metric_name?: string; minutes?: number }) => {
    const query = new URLSearchParams(params as any).toString();
    return fetchJson<TelemetryMetric[]>(`/telemetry/metrics${query ? `?${query}` : ""}`);
  },

  getLogs: (params?: { service?: string; level?: string; search?: string; limit?: number }) => {
    const query = new URLSearchParams(params as any).toString();
    return fetchJson<TelemetryLog[]>(`/telemetry/logs${query ? `?${query}` : ""}`);
  },

  // Simulator
  getScenarios: () => fetchJson<FailureScenario[]>("/simulator/scenarios"),

  injectScenario: (scenarioId: string, autoInvestigate: boolean = true) =>
    fetchJson<{
      injection: { incident_id: string; scenario: FailureScenario; status: string };
      investigation: any;
    }>("/simulator/inject", {
      method: "POST",
      body: JSON.stringify({ scenario_id: scenarioId, auto_investigate: autoInvestigate }),
    }),

  resetEnvironment: () =>
    fetchJson<{ status: string; message: string }>("/simulator/reset", { method: "POST" }),

  // Remediations
  getRemediations: (incidentId?: string) => {
    if (incidentId) {
      return fetchJson<RemediationAction[]>(`/remediations/incident/${incidentId}`);
    }
    return fetchJson<RemediationAction[]>("/remediations/");
  },

  approveRemediation: (actionId: string, approvedBy: string = "oncall-lead", executeNow: boolean = true) =>
    fetchJson<any>(`/remediations/${actionId}/approve`, {
      method: "POST",
      body: JSON.stringify({ approved_by: approvedBy, execute_now: executeNow }),
    }),

  rejectRemediation: (actionId: string, rejectedBy: string = "oncall-lead") =>
    fetchJson<any>(`/remediations/${actionId}/reject`, {
      method: "POST",
      body: JSON.stringify({ rejected_by: rejectedBy }),
    }),

  // Knowledge & RAG
  getRunbooks: (service?: string) =>
    fetchJson<Runbook[]>(`/knowledge/runbooks${service ? `?service=${service}` : ""}`),

  getPastIncidents: (service?: string) =>
    fetchJson<PastIncident[]>(`/knowledge/past-incidents${service ? `?service=${service}` : ""}`),

  searchKnowledge: (query: string, service?: string) =>
    fetchJson<{
      query: string;
      service?: string;
      runbooks: any[];
      past_incidents: any[];
    }>("/knowledge/search", {
      method: "POST",
      body: JSON.stringify({ query, service, top_k: 4 }),
    }),
};
