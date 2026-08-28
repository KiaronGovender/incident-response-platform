"use client";

import React, { useState } from "react";
import {
  Incident,
  InvestigationDetail,
  RemediationAction,
  TimelineItem,
} from "../lib/types";
import {
  AlertTriangle,
  CheckCircle,
  Clock,
  Cpu,
  Database,
  Terminal,
  ShieldCheck,
  ChevronDown,
  ChevronRight,
  Sparkles,
  Server,
  Play,
  RotateCcw,
  Layers,
  ArrowRight,
  GitCommit,
  Check,
  X,
  FileCode2,
} from "lucide-react";

interface IncidentDetailViewProps {
  incident: Incident;
  investigation: InvestigationDetail | null;
  remediations: RemediationAction[];
  timeline: TimelineItem[];
  onTriggerInvestigation: (incidentId: string) => void;
  onApproveRemediation: (actionId: string) => void;
  onRejectRemediation: (actionId: string) => void;
  isInvestigating: boolean;
  isExecutingAction: boolean;
}

export function IncidentDetailView({
  incident,
  investigation,
  remediations,
  timeline,
  onTriggerInvestigation,
  onApproveRemediation,
  onRejectRemediation,
  isInvestigating,
  isExecutingAction,
}: IncidentDetailViewProps) {
  const [expandedToolIndex, setExpandedToolIndex] = useState<number | null>(0);
  const [activeTab, setActiveTab] = useState<"investigation" | "timeline" | "remediation">("investigation");

  const getSeverityBadge = (severity: string) => {
    switch (severity.toLowerCase()) {
      case "critical":
        return "bg-rose-500/10 text-rose-400 border-rose-500/30";
      case "high":
        return "bg-amber-500/10 text-amber-400 border-amber-500/30";
      default:
        return "bg-blue-500/10 text-blue-400 border-blue-500/30";
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case "resolved":
        return "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
      case "mitigating":
        return "bg-cyan-500/10 text-cyan-400 border-cyan-500/30";
      case "investigating":
        return "bg-indigo-500/10 text-indigo-400 border-indigo-500/30 animate-pulse";
      default:
        return "bg-zinc-500/10 text-zinc-400 border-zinc-500/30";
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner & Metadata */}
      <div className="p-6 rounded-2xl bg-zinc-900/80 border border-zinc-800 shadow-xl backdrop-blur-sm">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2.5 mb-2">
              <span
                className={`px-2.5 py-0.5 rounded-full text-xs font-mono uppercase font-semibold border ${getSeverityBadge(
                  incident.severity
                )}`}
              >
                {incident.severity}
              </span>
              <span
                className={`px-2.5 py-0.5 rounded-full text-xs font-mono uppercase font-semibold border ${getStatusBadge(
                  incident.status
                )}`}
              >
                {incident.status}
              </span>
              <span className="text-xs font-mono text-zinc-500">ID: {incident.id}</span>
            </div>
            <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">{incident.title}</h1>
            <p className="text-sm text-zinc-400 mt-1 max-w-3xl">{incident.description}</p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="px-3.5 py-2 rounded-xl bg-zinc-950 border border-zinc-800/80 text-xs">
              <span className="text-zinc-500 block font-mono">AFFECTED SERVICE</span>
              <span className="text-white font-mono font-medium">{incident.service}</span>
            </div>

            {incident.status !== "resolved" && (
              <button
                onClick={() => onTriggerInvestigation(incident.id)}
                disabled={isInvestigating}
                className="flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white text-xs font-semibold shadow-lg shadow-indigo-500/25 transition disabled:opacity-50"
              >
                <Sparkles className={`w-4 h-4 ${isInvestigating ? "animate-spin" : ""}`} />
                <span>{isInvestigating ? "AI Investigating..." : "Run AI Investigation"}</span>
              </button>
            )}
          </div>
        </div>

        {/* Resolution Banner if resolved */}
        {incident.resolution_summary && (
          <div className="mt-4 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-300 flex items-start space-x-3">
            <CheckCircle className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold block text-emerald-200">Incident Resolved</span>
              <p className="mt-0.5">{incident.resolution_summary}</p>
            </div>
          </div>
        )}
      </div>

      {/* Sub-view Tab Navigation */}
      <div className="flex items-center space-x-2 border-b border-zinc-800 pb-2">
        <button
          onClick={() => setActiveTab("investigation")}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-medium transition ${
            activeTab === "investigation"
              ? "bg-zinc-800 text-white border border-zinc-700"
              : "text-zinc-400 hover:text-zinc-200"
          }`}
        >
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          <span>AI Investigation & Root Cause</span>
          {investigation?.hypotheses && (
            <span className="ml-1.5 px-1.5 py-0.5 text-[10px] rounded-full bg-indigo-500/20 text-indigo-300 font-mono">
              {investigation.hypotheses.length} Hypotheses
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab("remediation")}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-medium transition ${
            activeTab === "remediation"
              ? "bg-zinc-800 text-white border border-zinc-700"
              : "text-zinc-400 hover:text-zinc-200"
          }`}
        >
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>Controlled Remediation</span>
          {remediations.length > 0 && (
            <span className="ml-1.5 px-1.5 py-0.5 text-[10px] rounded-full bg-emerald-500/20 text-emerald-300 font-mono">
              {remediations.length} Actions
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab("timeline")}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-medium transition ${
            activeTab === "timeline"
              ? "bg-zinc-800 text-white border border-zinc-700"
              : "text-zinc-400 hover:text-zinc-200"
          }`}
        >
          <Clock className="w-3.5 h-3.5 text-amber-400" />
          <span>Incident Timeline</span>
          <span className="ml-1.5 px-1.5 py-0.5 text-[10px] rounded-full bg-zinc-700 text-zinc-300 font-mono">
            {timeline.length}
          </span>
        </button>
      </div>

      {/* ========================================================================= */}
      {/* TAB 1: AI INVESTIGATION & ROOT CAUSE */}
      {/* ========================================================================= */}
      {activeTab === "investigation" && (
        <div className="space-y-6">
          {investigation ? (
            <>
              {/* Executive Root Cause Card */}
              <div className="p-6 rounded-2xl bg-gradient-to-br from-indigo-950/40 via-zinc-900 to-zinc-900 border border-indigo-500/30 shadow-2xl relative overflow-hidden">
                <div className="absolute top-0 right-0 p-6 opacity-10 pointer-events-none">
                  <Sparkles className="w-48 h-48 text-indigo-400" />
                </div>
                <div className="relative z-10">
                  <div className="flex items-center justify-between flex-wrap gap-2 mb-3">
                    <div className="flex items-center space-x-2">
                      <span className="flex h-2.5 w-2.5 rounded-full bg-indigo-400 animate-ping"></span>
                      <span className="text-xs font-mono font-semibold uppercase text-indigo-300 tracking-wider">
                        AI Agent Root Cause Determination
                      </span>
                    </div>
                    {investigation.investigation.confidence_score && (
                      <div className="px-3 py-1 rounded-full bg-indigo-500/20 border border-indigo-500/30 text-xs font-mono font-bold text-indigo-300 flex items-center space-x-1.5">
                        <span>Confidence:</span>
                        <span className="text-white">
                          {Math.round(investigation.investigation.confidence_score * 100)}%
                        </span>
                      </div>
                    )}
                  </div>

                  <h3 className="text-lg sm:text-xl font-bold text-white mt-1">
                    {investigation.investigation.root_cause || "Analyzing evidence..."}
                  </h3>

                  {investigation.investigation.summary && (
                    <p className="text-xs sm:text-sm text-zinc-300 mt-2 leading-relaxed">
                      {investigation.investigation.summary}
                    </p>
                  )}

                  {investigation.investigation.recommended_remediation && (
                    <div className="mt-4 p-3.5 rounded-xl bg-zinc-950/80 border border-indigo-500/20 text-xs text-zinc-300">
                      <span className="text-indigo-400 font-semibold font-mono uppercase text-[11px] block mb-1">
                        Recommended Action
                      </span>
                      {investigation.investigation.recommended_remediation}
                    </div>
                  )}
                </div>
              </div>

              {/* Competing Hypotheses Grid */}
              <div>
                <h4 className="text-sm font-semibold text-zinc-200 uppercase font-mono tracking-wider mb-3 flex items-center space-x-2">
                  <Layers className="w-4 h-4 text-indigo-400" />
                  <span>Hypothesis Evaluation Matrix</span>
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {investigation.hypotheses.map((hyp) => {
                    const isConfirmed = hyp.status === "confirmed";
                    return (
                      <div
                        key={hyp.id}
                        className={`p-5 rounded-xl border transition-all ${
                          isConfirmed
                            ? "bg-emerald-950/20 border-emerald-500/40 shadow-lg shadow-emerald-500/5"
                            : "bg-zinc-900/60 border-zinc-800/80 opacity-75"
                        }`}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-mono uppercase font-bold ${
                              isConfirmed
                                ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                                : "bg-zinc-800 text-zinc-400"
                            }`}
                          >
                            {hyp.status}
                          </span>
                          <span className="text-xs font-mono font-medium text-zinc-400">
                            {Math.round(hyp.confidence * 100)}% match
                          </span>
                        </div>
                        <h5 className="text-sm font-bold text-white mb-1.5">{hyp.hypothesis}</h5>
                        <p className="text-xs text-zinc-400 leading-relaxed">{hyp.reasoning}</p>

                        {hyp.supporting_evidence && hyp.supporting_evidence.length > 0 && (
                          <div className="mt-3 space-y-1">
                            <span className="text-[10px] font-mono text-zinc-500 uppercase block">
                              Observed Evidence:
                            </span>
                            {hyp.supporting_evidence.map((ev, idx) => (
                              <div
                                key={idx}
                                className="text-[11px] text-emerald-300/90 font-mono flex items-start space-x-1.5"
                              >
                                <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                                <span>{ev}</span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* AI Diagnostic Tool Execution Traces */}
              <div>
                <h4 className="text-sm font-semibold text-zinc-200 uppercase font-mono tracking-wider mb-3 flex items-center space-x-2">
                  <Terminal className="w-4 h-4 text-violet-400" />
                  <span>Agent Diagnostic Tool Traces</span>
                </h4>
                <div className="space-y-3">
                  {investigation.tool_calls.map((tc, index) => {
                    const isExpanded = expandedToolIndex === index;
                    return (
                      <div
                        key={tc.id}
                        className="rounded-xl bg-zinc-900/90 border border-zinc-800 overflow-hidden transition"
                      >
                        <button
                          onClick={() => setExpandedToolIndex(isExpanded ? null : index)}
                          className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-zinc-800/40 transition"
                        >
                          <div className="flex items-center space-x-3">
                            <span className="w-5 h-5 rounded-full bg-zinc-800 text-[10px] font-mono font-bold text-zinc-300 flex items-center justify-center">
                              {tc.step_index}
                            </span>
                            <span className="font-mono text-xs font-semibold text-indigo-300">
                              {tc.tool_name}()
                            </span>
                            <span className="text-xs text-zinc-400 hidden sm:inline truncate max-w-md">
                              {tc.rationale}
                            </span>
                          </div>
                          {isExpanded ? (
                            <ChevronDown className="w-4 h-4 text-zinc-400" />
                          ) : (
                            <ChevronRight className="w-4 h-4 text-zinc-400" />
                          )}
                        </button>

                        {isExpanded && (
                          <div className="p-4 border-t border-zinc-800/80 bg-zinc-950/60 space-y-3 text-xs">
                            {tc.rationale && (
                              <p className="text-zinc-300 text-xs">
                                <span className="font-semibold text-zinc-400 font-mono">Agent Rationale: </span>
                                {tc.rationale}
                              </p>
                            )}

                            <div>
                              <span className="text-[10px] font-mono text-zinc-500 uppercase block mb-1">
                                Input Parameters:
                              </span>
                              <pre className="p-2.5 rounded-lg bg-zinc-900 border border-zinc-800 text-[11px] font-mono text-zinc-300 overflow-x-auto">
                                {JSON.stringify(tc.parameters, null, 2)}
                              </pre>
                            </div>

                            <div>
                              <span className="text-[10px] font-mono text-zinc-500 uppercase block mb-1">
                                Tool Execution Output:
                              </span>
                              <pre className="p-2.5 rounded-lg bg-zinc-900 border border-zinc-800 text-[11px] font-mono text-emerald-400/90 overflow-x-auto max-h-60">
                                {JSON.stringify(tc.result, null, 2)}
                              </pre>
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </>
          ) : (
            <div className="p-12 text-center rounded-2xl bg-zinc-900/40 border border-zinc-800 space-y-4">
              <Sparkles className="w-10 h-10 text-indigo-400 mx-auto animate-bounce" />
              <div>
                <h3 className="text-base font-bold text-white">No AI Investigation Run Yet</h3>
                <p className="text-xs text-zinc-400 mt-1 max-w-md mx-auto">
                  Click the button below to launch the autonomous investigation agent. It will inspect logs, metrics,
                  service dependencies, evaluate candidate hypotheses, and formulate a root cause.
                </p>
              </div>
              <button
                onClick={() => onTriggerInvestigation(incident.id)}
                disabled={isInvestigating}
                className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition shadow-lg shadow-indigo-500/25"
              >
                {isInvestigating ? "Investigating..." : "Launch Autonomous Agent"}
              </button>
            </div>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: CONTROLLED REMEDIATION CONSOLE */}
      {/* ========================================================================= */}
      {activeTab === "remediation" && (
        <div className="space-y-6">
          <div>
            <h3 className="text-sm font-semibold text-zinc-200 uppercase font-mono tracking-wider mb-2">
              Controlled Human-in-the-Loop Remediation
            </h3>
            <p className="text-xs text-zinc-400 max-w-2xl">
              Production actions (such as container rollbacks and service restarts) require explicit human approval to
              prevent unintended disruptions.
            </p>
          </div>

          {remediations.length > 0 ? (
            <div className="space-y-4">
              {remediations.map((rem) => {
                const isProposed = rem.status === "proposed";
                const isVerified = rem.status === "verified";
                const isExecuting = rem.status === "executing";

                return (
                  <div
                    key={rem.id}
                    className={`p-6 rounded-2xl border transition ${
                      isVerified
                        ? "bg-emerald-950/20 border-emerald-500/30"
                        : isProposed
                        ? "bg-zinc-900 border-indigo-500/40 shadow-xl"
                        : "bg-zinc-900/60 border-zinc-800"
                    }`}
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
                      <div className="flex items-center space-x-2">
                        <span
                          className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono uppercase font-bold border ${
                            rem.risk_level === "high"
                              ? "bg-rose-500/10 text-rose-400 border-rose-500/30"
                              : rem.risk_level === "medium"
                              ? "bg-amber-500/10 text-amber-400 border-amber-500/30"
                              : "bg-blue-500/10 text-blue-400 border-blue-500/30"
                          }`}
                        >
                          Risk: {rem.risk_level}
                        </span>
                        <span
                          className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono uppercase font-bold border ${
                            isVerified
                              ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
                              : "bg-zinc-800 text-zinc-300 border-zinc-700"
                          }`}
                        >
                          {rem.status}
                        </span>
                      </div>
                      <span className="text-xs font-mono text-zinc-500">ID: {rem.id}</span>
                    </div>

                    <h4 className="text-lg font-bold text-white">{rem.title}</h4>
                    <p className="text-xs sm:text-sm text-zinc-300 mt-1">{rem.description}</p>

                    {/* Parameters summary */}
                    <div className="mt-3 p-3 rounded-lg bg-zinc-950/80 border border-zinc-800 text-xs font-mono text-zinc-400">
                      <span className="text-zinc-500 block mb-1">Execution Parameters:</span>
                      <pre className="text-[11px] text-indigo-300">
                        {JSON.stringify(rem.parameters, null, 2)}
                      </pre>
                    </div>

                    {/* Output logs & Verification if executed */}
                    {rem.execution_output && (
                      <div className="mt-3 p-3 rounded-lg bg-zinc-950 border border-zinc-800 text-xs font-mono text-zinc-300">
                        <span className="text-zinc-500 block mb-0.5">Execution Log:</span>
                        <p className="text-emerald-400">{rem.execution_output}</p>
                      </div>
                    )}

                    {rem.verification_result && (
                      <div className="mt-3 p-3 rounded-lg bg-emerald-950/40 border border-emerald-500/30 text-xs text-emerald-300 flex items-start space-x-2">
                        <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                        <p>{rem.verification_result}</p>
                      </div>
                    )}

                    {/* Action buttons */}
                    {isProposed && (
                      <div className="mt-5 flex items-center space-x-3">
                        <button
                          onClick={() => onApproveRemediation(rem.id)}
                          disabled={isExecutingAction}
                          className="flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition shadow-lg shadow-emerald-600/20 disabled:opacity-50"
                        >
                          <Play className={`w-3.5 h-3.5 ${isExecutingAction ? "animate-spin" : ""}`} />
                          <span>{isExecutingAction ? "Executing..." : "Approve & Execute Remediation"}</span>
                        </button>
                        <button
                          onClick={() => onRejectRemediation(rem.id)}
                          disabled={isExecutingAction}
                          className="flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs font-medium transition border border-zinc-700"
                        >
                          <X className="w-3.5 h-3.5" />
                          <span>Reject</span>
                        </button>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="p-8 text-center rounded-2xl bg-zinc-900/40 border border-zinc-800 text-xs text-zinc-400">
              No remediation actions proposed yet. Run the AI investigation to generate validated remediation proposals.
            </div>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 3: UNIFIED INCIDENT TIMELINE */}
      {/* ========================================================================= */}
      {activeTab === "timeline" && (
        <div className="p-6 rounded-2xl bg-zinc-900/80 border border-zinc-800">
          <h3 className="text-sm font-semibold text-zinc-200 uppercase font-mono tracking-wider mb-6">
            Unified Chronological Timeline
          </h3>

          <div className="relative border-l border-zinc-800 ml-4 space-y-8">
            {timeline.map((item, idx) => (
              <div key={idx} className="relative pl-6">
                {/* Timeline node icon */}
                <div className="absolute -left-2.5 top-1.5 w-5 h-5 rounded-full bg-zinc-900 border border-indigo-500/50 flex items-center justify-center shadow">
                  <div className="w-2 h-2 rounded-full bg-indigo-400" />
                </div>

                <div className="flex items-center space-x-3 mb-1">
                  <span className="text-[11px] font-mono text-zinc-500">
                    {new Date(item.timestamp).toLocaleTimeString()}
                  </span>
                  <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-zinc-800 text-zinc-400">
                    {item.type}
                  </span>
                  <span className="text-[11px] font-mono text-zinc-500">[{item.source}]</span>
                </div>

                <h5 className="text-sm font-semibold text-white">{item.title}</h5>

                {item.details && typeof item.details === "object" && Object.keys(item.details).length > 0 && (
                  <pre className="mt-2 p-2.5 rounded-lg bg-zinc-950 border border-zinc-800/80 text-[11px] font-mono text-zinc-400 overflow-x-auto">
                    {JSON.stringify(item.details, null, 2)}
                  </pre>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
