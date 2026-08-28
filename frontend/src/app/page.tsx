"use client";

import React, { useState, useEffect, useCallback } from "react";
import { api } from "../lib/api";
import {
  Incident,
  InvestigationDetail,
  RemediationAction,
  Service,
  TelemetryMetric,
  TelemetryLog,
  FailureScenario,
  Runbook,
  PastIncident,
  TimelineItem,
} from "../lib/types";
import { Navbar } from "../components/Navbar";
import { IncidentDetailView } from "../components/IncidentDetailView";
import { SimulatorView } from "../components/SimulatorView";
import { TelemetryView } from "../components/TelemetryView";
import { KnowledgeView } from "../components/KnowledgeView";
import {
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Search,
  Filter,
  Plus,
  RefreshCw,
  Sparkles,
  Zap,
} from "lucide-react";

export default function Home() {
  const [activeTab, setActiveTab] = useState<"incidents" | "simulator" | "telemetry" | "knowledge">("incidents");
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [investigation, setInvestigation] = useState<InvestigationDetail | null>(null);
  const [remediations, setRemediations] = useState<RemediationAction[]>([]);
  const [timeline, setTimeline] = useState<TimelineItem[]>([]);

  const [services, setServices] = useState<Service[]>([]);
  const [metrics, setMetrics] = useState<TelemetryMetric[]>([]);
  const [logs, setLogs] = useState<TelemetryLog[]>([]);
  const [scenarios, setScenarios] = useState<FailureScenario[]>([]);
  const [runbooks, setRunbooks] = useState<Runbook[]>([]);
  const [pastIncidents, setPastIncidents] = useState<PastIncident[]>([]);
  const [systemHealth, setSystemHealth] = useState<{ status: string; version: string; ai_engine: string } | null>(null);

  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [searchFilter, setSearchFilter] = useState<string>("");

  const [isInvestigating, setIsInvestigating] = useState(false);
  const [isExecutingAction, setIsExecutingAction] = useState(false);
  const [isInjecting, setIsInjecting] = useState(false);
  const [isResetting, setIsResetting] = useState(false);

  // 1. Fetch initial data and health
  const refreshGlobalData = useCallback(async () => {
    try {
      const [health, incs, srvs, mets, lgs, scens, rbs, pasts] = await Promise.all([
        api.getHealth().catch(() => null),
        api.getIncidents().catch(() => []),
        api.getServices().catch(() => []),
        api.getMetrics().catch(() => []),
        api.getLogs().catch(() => []),
        api.getScenarios().catch(() => []),
        api.getRunbooks().catch(() => []),
        api.getPastIncidents().catch(() => []),
      ]);

      if (health) setSystemHealth(health);
      setIncidents(incs);
      setServices(srvs);
      setMetrics(mets);
      setLogs(lgs);
      setScenarios(scens);
      setRunbooks(rbs);
      setPastIncidents(pasts);

      // Default select the first incident if none selected
      if (!selectedIncident && incs.length > 0) {
        setSelectedIncident(incs[0]);
      }
    } catch (err) {
      console.error("Failed refreshing dashboard data:", err);
    }
  }, [selectedIncident]);

  // 2. Fetch details for selected incident
  const refreshIncidentDetails = useCallback(async (incidentId: string) => {
    try {
      const [inv, rems, tl, inc] = await Promise.all([
        api.getInvestigationByIncident(incidentId).catch(() => null),
        api.getRemediations(incidentId).catch(() => []),
        api.getIncidentTimeline(incidentId).catch(() => ({ timeline: [] })),
        api.getIncident(incidentId).catch(() => null),
      ]);

      setInvestigation(inv);
      setRemediations(rems);
      setTimeline(tl.timeline || []);
      if (inc) setSelectedIncident(inc);
    } catch (err) {
      console.error("Failed fetching incident details:", err);
    }
  }, []);

  useEffect(() => {
    refreshGlobalData();
    const interval = setInterval(refreshGlobalData, 4000);
    return () => clearInterval(interval);
  }, [refreshGlobalData]);

  useEffect(() => {
    if (selectedIncident) {
      refreshIncidentDetails(selectedIncident.id);
    }
  }, [selectedIncident?.id, refreshIncidentDetails]);

  // Handler: Trigger AI Investigation
  const handleTriggerInvestigation = async (incidentId: string) => {
    setIsInvestigating(true);
    try {
      await api.triggerInvestigation(incidentId);
      await refreshIncidentDetails(incidentId);
      await refreshGlobalData();
    } catch (err) {
      alert(`Investigation failed: ${err}`);
    } finally {
      setIsInvestigating(false);
    }
  };

  // Handler: Approve Remediation
  const handleApproveRemediation = async (actionId: string) => {
    setIsExecutingAction(true);
    try {
      await api.approveRemediation(actionId, "oncall-lead", true);
      if (selectedIncident) {
        await refreshIncidentDetails(selectedIncident.id);
      }
      await refreshGlobalData();
    } catch (err) {
      alert(`Remediation execution failed: ${err}`);
    } finally {
      setIsExecutingAction(false);
    }
  };

  // Handler: Reject Remediation
  const handleRejectRemediation = async (actionId: string) => {
    setIsExecutingAction(true);
    try {
      await api.rejectRemediation(actionId, "oncall-lead");
      if (selectedIncident) {
        await refreshIncidentDetails(selectedIncident.id);
      }
      await refreshGlobalData();
    } catch (err) {
      alert(`Remediation rejection failed: ${err}`);
    } finally {
      setIsExecutingAction(false);
    }
  };

  // Handler: Inject Failure Scenario
  const handleInjectScenario = async (scenarioId: string) => {
    setIsInjecting(true);
    try {
      const res = await api.injectScenario(scenarioId, true);
      await refreshGlobalData();
      if (res.injection?.incident_id) {
        const newInc = await api.getIncident(res.injection.incident_id);
        setSelectedIncident(newInc);
        await refreshIncidentDetails(newInc.id);
        setActiveTab("incidents");
      }
    } catch (err) {
      alert(`Failure injection failed: ${err}`);
    } finally {
      setIsInjecting(false);
    }
  };

  // Handler: Reset Environment
  const handleResetEnvironment = async () => {
    setIsResetting(true);
    try {
      await api.resetEnvironment();
      await refreshGlobalData();
      if (selectedIncident) {
        await refreshIncidentDetails(selectedIncident.id);
      }
    } catch (err) {
      alert(`Reset failed: ${err}`);
    } finally {
      setIsResetting(false);
    }
  };

  // Filtered incidents
  const filteredIncidents = incidents.filter((inc) => {
    const matchesStatus = statusFilter === "all" || inc.status.toLowerCase() === statusFilter.toLowerCase();
    const matchesSearch =
      searchFilter === "" ||
      inc.title.toLowerCase().includes(searchFilter.toLowerCase()) ||
      inc.service.toLowerCase().includes(searchFilter.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 selection:bg-indigo-500 selection:text-white flex flex-col font-sans">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        systemHealth={systemHealth}
        onReset={handleResetEnvironment}
        isResetting={isResetting}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === "incidents" && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
            {/* Left Sidebar: Incidents Feed */}
            <div className="lg:col-span-4 space-y-4">
              <div className="p-4 rounded-2xl bg-zinc-900/80 border border-zinc-800 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <ShieldAlert className="w-4 h-4 text-indigo-400" />
                    <h2 className="text-sm font-bold text-white uppercase font-mono tracking-wider">Incidents Feed</h2>
                  </div>
                  <span className="px-2 py-0.5 rounded-full text-xs font-mono bg-zinc-800 text-zinc-300 font-semibold">
                    {filteredIncidents.length}
                  </span>
                </div>

                {/* Filter Pills */}
                <div className="flex items-center space-x-1 overflow-x-auto pb-1 text-[11px]">
                  {["all", "open", "investigating", "mitigating", "resolved"].map((st) => (
                    <button
                      key={st}
                      onClick={() => setStatusFilter(st)}
                      className={`px-2.5 py-1 rounded-lg font-mono uppercase transition ${
                        statusFilter === st
                          ? "bg-indigo-600 text-white font-bold"
                          : "text-zinc-400 hover:text-zinc-200 bg-zinc-950"
                      }`}
                    >
                      {st}
                    </button>
                  ))}
                </div>

                {/* Search box */}
                <div className="relative">
                  <Search className="w-3.5 h-3.5 text-zinc-500 absolute left-3 top-2.5" />
                  <input
                    type="text"
                    placeholder="Search incidents or services..."
                    value={searchFilter}
                    onChange={(e) => setSearchFilter(e.target.value)}
                    className="w-full pl-8 pr-3 py-1.5 rounded-lg bg-zinc-950 border border-zinc-800 text-xs text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              {/* Incidents Scrollable List */}
              <div className="space-y-2.5 max-h-[700px] overflow-y-auto pr-1">
                {filteredIncidents.map((inc) => {
                  const isSelected = selectedIncident?.id === inc.id;
                  const isCritical = inc.severity.toLowerCase() === "critical";
                  const isResolved = inc.status.toLowerCase() === "resolved";
                  const isInvestigatingInc = inc.status.toLowerCase() === "investigating";

                  return (
                    <div
                      key={inc.id}
                      onClick={() => setSelectedIncident(inc)}
                      className={`p-4 rounded-xl border cursor-pointer transition text-left ${
                        isSelected
                          ? "bg-indigo-950/40 border-indigo-500/80 shadow-lg shadow-indigo-500/10"
                          : "bg-zinc-900/60 border-zinc-800/80 hover:bg-zinc-900 hover:border-zinc-700"
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1.5">
                        <div className="flex items-center space-x-1.5">
                          <span
                            className={`w-2 h-2 rounded-full ${
                              isResolved
                                ? "bg-emerald-400"
                                : isCritical
                                ? "bg-rose-500 animate-pulse"
                                : "bg-amber-400"
                            }`}
                          />
                          <span className="text-xs font-mono font-bold text-zinc-300">{inc.service}</span>
                        </div>
                        <span className="text-[10px] font-mono text-zinc-500">
                          {new Date(inc.created_at).toLocaleTimeString()}
                        </span>
                      </div>

                      <h3 className="text-xs sm:text-sm font-semibold text-white line-clamp-1">{inc.title}</h3>

                      <div className="flex items-center justify-between mt-2 pt-2 border-t border-zinc-800/50">
                        <span
                          className={`text-[10px] font-mono uppercase px-1.5 py-0.5 rounded ${
                            isCritical
                              ? "bg-rose-500/15 text-rose-400"
                              : "bg-amber-500/15 text-amber-400"
                          }`}
                        >
                          {inc.severity}
                        </span>

                        <span
                          className={`text-[10px] font-mono uppercase px-1.5 py-0.5 rounded ${
                            isResolved
                              ? "bg-emerald-500/15 text-emerald-400"
                              : isInvestigatingInc
                              ? "bg-indigo-500/15 text-indigo-400"
                              : "bg-zinc-800 text-zinc-400"
                          }`}
                        >
                          {inc.status}
                        </span>
                      </div>
                    </div>
                  );
                })}

                {filteredIncidents.length === 0 && (
                  <div className="p-8 text-center rounded-xl bg-zinc-900/40 border border-zinc-800 text-xs text-zinc-500">
                    No incidents match the active filter.
                  </div>
                )}
              </div>
            </div>

            {/* Right Pane: Incident Detail Cockpit */}
            <div className="lg:col-span-8">
              {selectedIncident ? (
                <IncidentDetailView
                  incident={selectedIncident}
                  investigation={investigation}
                  remediations={remediations}
                  timeline={timeline}
                  onTriggerInvestigation={handleTriggerInvestigation}
                  onApproveRemediation={handleApproveRemediation}
                  onRejectRemediation={handleRejectRemediation}
                  isInvestigating={isInvestigating}
                  isExecutingAction={isExecutingAction}
                />
              ) : (
                <div className="p-16 text-center rounded-2xl bg-zinc-900/40 border border-zinc-800 space-y-3">
                  <Zap className="w-10 h-10 text-zinc-600 mx-auto" />
                  <h3 className="text-base font-bold text-white">No Incident Selected</h3>
                  <p className="text-xs text-zinc-400">Select an incident from the feed or inject a failure scenario.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "simulator" && (
          <SimulatorView
            scenarios={scenarios}
            onInject={handleInjectScenario}
            isInjecting={isInjecting}
          />
        )}

        {activeTab === "telemetry" && (
          <TelemetryView
            services={services}
            metrics={metrics}
            logs={logs}
            onRefreshLogs={async (level, search) => {
              const lgs = await api.getLogs({ level, search });
              setLogs(lgs);
            }}
          />
        )}

        {activeTab === "knowledge" && (
          <KnowledgeView
            runbooks={runbooks}
            pastIncidents={pastIncidents}
            onSearch={(query) => api.searchKnowledge(query)}
          />
        )}
      </main>
    </div>
  );
}
