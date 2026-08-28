export type IncidentSeverity = "low" | "medium" | "high" | "critical";
export type IncidentStatus = "open" | "investigating" | "mitigating" | "resolved";

export interface Incident {
  id: string;
  title: string;
  description: string;
  service: string;
  severity: IncidentSeverity;
  status: IncidentStatus;
  root_cause?: string | null;
  resolution_summary?: string | null;
  confidence_score?: number | null;
  created_at: string;
  updated_at: string;
  detection_time?: string | null;
  resolved_at?: string | null;
}

export type EventType =
  | "log"
  | "metric"
  | "alert"
  | "deployment"
  | "infrastructure"
  | "configuration"
  | "database"
  | "service_health"
  | "agent_action";

export interface IncidentEvent {
  id: string;
  incident_id: string;
  event_type: EventType;
  source: string;
  message: string;
  timestamp: string;
  data: Record<string, any>;
}

export interface TimelineItem {
  type: string;
  timestamp: string;
  title: string;
  details: any;
  source: string;
  severity?: string;
}

export type HypothesisStatus = "exploring" | "confirmed" | "refuted";

export interface InvestigationHypothesis {
  id: string;
  investigation_id: string;
  hypothesis: string;
  status: HypothesisStatus;
  confidence: number;
  reasoning?: string | null;
  supporting_evidence: string[];
  refuting_evidence: string[];
  created_at: string;
}

export interface InvestigationToolCall {
  id: string;
  investigation_id: string;
  step_index: number;
  tool_name: string;
  parameters: Record<string, any>;
  result: Record<string, any>;
  rationale?: string | null;
  timestamp: string;
}

export interface Investigation {
  id: string;
  incident_id: string;
  status: "pending" | "running" | "completed" | "failed";
  current_hypothesis?: string | null;
  confidence_score?: number | null;
  root_cause?: string | null;
  summary?: string | null;
  recommended_remediation?: string | null;
  created_at: string;
  updated_at: string;
}

export interface InvestigationDetail {
  investigation: Investigation;
  hypotheses: InvestigationHypothesis[];
  tool_calls: InvestigationToolCall[];
}

export type ServiceStatus = "healthy" | "degraded" | "failing";

export interface Service {
  id: string;
  name: string;
  environment: string;
  owner: string;
  repository: string;
  current_version: string;
  status: ServiceStatus;
  dependencies: string[];
  health_check_url?: string | null;
  created_at: string;
}

export interface Deployment {
  id: string;
  service: string;
  version: string;
  commit_hash: string;
  deployed_by: string;
  status: "successful" | "failed" | "rolled_back";
  timestamp: string;
  changes_summary?: string | null;
  rollback_version?: string | null;
}

export interface TelemetryMetric {
  id: string;
  service: string;
  metric_name: string;
  value: number;
  unit: string;
  timestamp: string;
}

export interface TelemetryLog {
  id: string;
  service: string;
  level: "DEBUG" | "INFO" | "WARN" | "ERROR" | "CRITICAL";
  message: string;
  timestamp: string;
  trace_id?: string | null;
  metadata?: Record<string, any>;
}

export interface RemediationAction {
  id: string;
  incident_id: string;
  action_type: string;
  title: string;
  description: string;
  risk_level: "low" | "medium" | "high";
  status: "proposed" | "approved" | "rejected" | "executing" | "executed" | "verified" | "failed";
  parameters: Record<string, any>;
  approved_by?: string | null;
  execution_output?: string | null;
  verification_result?: string | null;
  created_at: string;
  executed_at?: string | null;
}

export interface FailureScenario {
  id: string;
  title: string;
  service: string;
  severity: string;
  description: string;
  expected_root_cause: string;
  expected_remediation: string;
}

export interface Runbook {
  id: string;
  title: string;
  service: string;
  trigger_patterns: string[];
  diagnosis_steps: string[];
  remediation_actions: string[];
  risk_level: string;
  content: string;
  tags: string[];
}

export interface PastIncident {
  id: string;
  title: string;
  service: string;
  root_cause: string;
  resolution: string;
  symptoms: string[];
  postmortem_url?: string | null;
}
