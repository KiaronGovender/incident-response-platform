"use client";

import React, { useState } from "react";
import { Service, TelemetryMetric, TelemetryLog } from "../lib/types";
import { Activity, Server, Database, GitBranch, Search, Filter, AlertTriangle, ShieldCheck } from "lucide-react";

interface TelemetryViewProps {
  services: Service[];
  metrics: TelemetryMetric[];
  logs: TelemetryLog[];
  onRefreshLogs: (level?: string, search?: string) => void;
}

export function TelemetryView({ services, metrics, logs, onRefreshLogs }: TelemetryViewProps) {
  const [selectedLevel, setSelectedLevel] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const handleFilterChange = (level: string) => {
    setSelectedLevel(level);
    onRefreshLogs(level === "ALL" ? undefined : level, searchQuery || undefined);
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    onRefreshLogs(selectedLevel === "ALL" ? undefined : selectedLevel, searchQuery || undefined);
  };

  return (
    <div className="space-y-6">
      {/* Topology Map */}
      <div>
        <h3 className="text-sm font-semibold text-zinc-200 uppercase font-mono tracking-wider mb-3 flex items-center space-x-2">
          <Server className="w-4 h-4 text-indigo-400" />
          <span>Microservices Fleet Topology</span>
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {services.map((srv) => {
            const isFailing = srv.status === "failing";
            const isDegraded = srv.status === "degraded";
            return (
              <div
                key={srv.id}
                className={`p-4 rounded-xl border transition ${
                  isFailing
                    ? "bg-rose-950/20 border-rose-500/40 shadow-lg shadow-rose-500/5"
                    : isDegraded
                    ? "bg-amber-950/20 border-amber-500/40"
                    : "bg-zinc-900/80 border-zinc-800"
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-bold text-sm text-white font-mono">{srv.name}</span>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-mono uppercase font-bold ${
                      isFailing
                        ? "bg-rose-500/20 text-rose-300"
                        : isDegraded
                        ? "bg-amber-500/20 text-amber-300"
                        : "bg-emerald-500/20 text-emerald-300"
                    }`}
                  >
                    {srv.status}
                  </span>
                </div>

                <div className="space-y-1 text-xs text-zinc-400 font-mono">
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Version:</span>
                    <span className="text-zinc-300">{srv.current_version}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Owner:</span>
                    <span className="text-zinc-300">{srv.owner}</span>
                  </div>
                  {srv.dependencies && srv.dependencies.length > 0 && (
                    <div className="pt-2">
                      <span className="text-[10px] text-zinc-500 uppercase block mb-1">Dependencies:</span>
                      <div className="flex flex-wrap gap-1">
                        {srv.dependencies.map((dep, i) => (
                          <span
                            key={i}
                            className="px-1.5 py-0.5 rounded bg-zinc-800 text-[10px] text-zinc-300 font-mono"
                          >
                            {dep}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Metrics Summary Grid */}
      <div>
        <h3 className="text-sm font-semibold text-zinc-200 uppercase font-mono tracking-wider mb-3 flex items-center space-x-2">
          <Activity className="w-4 h-4 text-emerald-400" />
          <span>Real-Time Production Metrics</span>
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {metrics.slice(0, 8).map((m) => (
            <div key={m.id} className="p-4 rounded-xl bg-zinc-900/80 border border-zinc-800">
              <div className="flex items-center justify-between text-xs text-zinc-400 mb-1">
                <span className="font-mono">{m.service}</span>
                <span className="text-[10px] text-zinc-500">{new Date(m.timestamp).toLocaleTimeString()}</span>
              </div>
              <div className="text-lg font-bold text-white font-mono">
                {m.value.toFixed(1)} <span className="text-xs text-zinc-500 font-normal">{m.unit}</span>
              </div>
              <span className="text-[11px] text-zinc-500 font-mono">{m.metric_name}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Structured Log Stream */}
      <div className="p-6 rounded-2xl bg-zinc-900/80 border border-zinc-800">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
          <h3 className="text-sm font-semibold text-zinc-200 uppercase font-mono tracking-wider">
            Application & System Log Stream
          </h3>

          <form onSubmit={handleSearch} className="flex items-center space-x-2">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-zinc-500 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search log messages..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8 pr-3 py-1.5 rounded-lg bg-zinc-950 border border-zinc-800 text-xs text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-indigo-500 w-48 sm:w-64"
              />
            </div>

            <div className="flex items-center space-x-1 bg-zinc-950 border border-zinc-800 p-1 rounded-lg text-[11px]">
              {["ALL", "CRITICAL", "ERROR", "WARN", "INFO"].map((lvl) => (
                <button
                  key={lvl}
                  type="button"
                  onClick={() => handleFilterChange(lvl)}
                  className={`px-2 py-1 rounded font-mono ${
                    selectedLevel === lvl ? "bg-indigo-600 text-white font-bold" : "text-zinc-400 hover:text-zinc-200"
                  }`}
                >
                  {lvl}
                </button>
              ))}
            </div>
          </form>
        </div>

        <div className="space-y-2 max-h-96 overflow-y-auto font-mono text-xs">
          {logs.map((log) => {
            const isCritical = log.level === "CRITICAL";
            const isError = log.level === "ERROR";
            const isWarn = log.level === "WARN";
            return (
              <div
                key={log.id}
                className={`p-3 rounded-lg border transition ${
                  isCritical
                    ? "bg-rose-950/30 border-rose-500/30 text-rose-300"
                    : isError
                    ? "bg-rose-950/15 border-rose-500/20 text-rose-300"
                    : isWarn
                    ? "bg-amber-950/15 border-amber-500/20 text-amber-300"
                    : "bg-zinc-950 border-zinc-800/80 text-zinc-300"
                }`}
              >
                <div className="flex items-center justify-between text-[10px] text-zinc-500 mb-1">
                  <span>
                    [{new Date(log.timestamp).toLocaleTimeString()}] [{log.service}] {log.trace_id ? `[trace:${log.trace_id}]` : ""}
                  </span>
                  <span
                    className={`font-bold ${
                      isCritical || isError ? "text-rose-400" : isWarn ? "text-amber-400" : "text-zinc-400"
                    }`}
                  >
                    {log.level}
                  </span>
                </div>
                <p className="break-all">{log.message}</p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
