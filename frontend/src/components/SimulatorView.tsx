"use client";

import React from "react";
import { FailureScenario } from "../lib/types";
import { Cpu, AlertTriangle, Play, Sparkles, RefreshCw, Layers, ShieldAlert, CheckCircle2 } from "lucide-react";

interface SimulatorViewProps {
  scenarios: FailureScenario[];
  onInject: (scenarioId: string) => void;
  isInjecting: boolean;
}

export function SimulatorView({ scenarios, onInject, isInjecting }: SimulatorViewProps) {
  return (
    <div className="space-y-6">
      {/* Intro Header */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-zinc-900 via-zinc-900 to-indigo-950/40 border border-zinc-800">
        <div className="flex items-center space-x-3 mb-2">
          <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <Cpu className="w-5 h-5" />
          </div>
          <h2 className="text-lg font-bold text-white tracking-tight">Production Environment Failure Lab</h2>
        </div>
        <p className="text-xs sm:text-sm text-zinc-400 max-w-3xl leading-relaxed">
          Inject real-world production failure scenarios into the microservices fleet. The platform will automatically
          detect the SLA violations, ingest telemetry, correlate alerts, launch the AI investigation agent, formulate
          competing hypotheses, and suggest verified remediations.
        </p>
      </div>

      {/* Scenarios Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {scenarios.map((scenario) => {
          const isCritical = scenario.severity.toLowerCase() === "critical";
          return (
            <div
              key={scenario.id}
              className="p-5 rounded-2xl bg-zinc-900/80 border border-zinc-800 hover:border-zinc-700 transition shadow-lg flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span
                    className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono uppercase font-bold border ${
                      isCritical
                        ? "bg-rose-500/10 text-rose-400 border-rose-500/30"
                        : "bg-amber-500/10 text-amber-400 border-amber-500/30"
                    }`}
                  >
                    {scenario.severity}
                  </span>
                  <span className="text-xs font-mono text-zinc-500">{scenario.service}</span>
                </div>

                <h3 className="text-base font-bold text-white mb-2">{scenario.title}</h3>
                <p className="text-xs text-zinc-400 leading-relaxed mb-4">{scenario.description}</p>

                <div className="p-3 rounded-xl bg-zinc-950 border border-zinc-800/80 space-y-2 text-[11px] mb-4">
                  <div>
                    <span className="text-zinc-500 font-mono uppercase block text-[10px]">Expected Root Cause:</span>
                    <span className="text-zinc-300">{scenario.expected_root_cause}</span>
                  </div>
                  <div>
                    <span className="text-zinc-500 font-mono uppercase block text-[10px]">Safe Remediation:</span>
                    <span className="text-emerald-400/90">{scenario.expected_remediation}</span>
                  </div>
                </div>
              </div>

              <button
                onClick={() => onInject(scenario.id)}
                disabled={isInjecting}
                className="w-full flex items-center justify-center space-x-2 py-2.5 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/20 transition disabled:opacity-50"
              >
                <Play className={`w-3.5 h-3.5 ${isInjecting ? "animate-spin" : ""}`} />
                <span>{isInjecting ? "Injecting & Launching AI..." : "Inject Failure Scenario"}</span>
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
