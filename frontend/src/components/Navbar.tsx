"use client";

import React from "react";
import {
  ShieldAlert,
  Activity,
  Cpu,
  BookOpen,
  RefreshCw,
  Zap,
  CheckCircle2,
} from "lucide-react";

interface NavbarProps {
  activeTab: "incidents" | "simulator" | "telemetry" | "knowledge";
  setActiveTab: (
    tab: "incidents" | "simulator" | "telemetry" | "knowledge",
  ) => void;
  systemHealth: { status: string; version: string; ai_engine: string } | null;
  onReset: () => void;
  isResetting: boolean;
}

export function Navbar({
  activeTab,
  setActiveTab,
  systemHealth,
  onReset,
  isResetting,
}: NavbarProps) {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-zinc-800/80 bg-zinc-950/90 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between py-3.5 gap-3.5">
          {/* Logo & Platform Branding */}
          <div className="flex items-center space-x-3.5">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-violet-600 to-cyan-400 p-[1px] shadow-lg shadow-indigo-500/20 shrink-0">
              <div className="w-full h-full bg-zinc-950 rounded-[11px] flex items-center justify-center">
                <Zap className="w-5 h-5 text-indigo-400" />
              </div>
            </div>

            <div className="flex flex-col justify-center">
              <div className="flex items-center space-x-2.5">
                <span className="font-extrabold text-base tracking-tight text-white leading-tight">
                  AUTONOMOUS INCIDENT RESPONSE
                </span>
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded-md bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-semibold">
                  AI SRE
                </span>
              </div>
              <p className="text-[11px] text-zinc-400 font-mono tracking-tight mt-0.5">
                Root Cause Analysis & Controlled Remediation Platform
              </p>
            </div>
          </div>

          {/* Center Navigation Tabs */}
          <nav className="flex items-center space-x-1.5 bg-zinc-900/90 border border-zinc-800 p-1 rounded-xl overflow-x-auto self-start md:self-auto max-w-full">
            <button
              onClick={() => setActiveTab("incidents")}
              className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all whitespace-nowrap ${
                activeTab === "incidents"
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/60"
              }`}
            >
              <ShieldAlert className="w-3.5 h-3.5" />
              <span>Incident Command</span>
            </button>

            <button
              onClick={() => setActiveTab("simulator")}
              className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all whitespace-nowrap ${
                activeTab === "simulator"
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/60"
              }`}
            >
              <Cpu className="w-3.5 h-3.5" />
              <span>Failure Lab</span>
            </button>

            <button
              onClick={() => setActiveTab("telemetry")}
              className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all whitespace-nowrap ${
                activeTab === "telemetry"
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/60"
              }`}
            >
              <Activity className="w-3.5 h-3.5" />
              <span>Observability</span>
            </button>

            <button
              onClick={() => setActiveTab("knowledge")}
              className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all whitespace-nowrap ${
                activeTab === "knowledge"
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/60"
              }`}
            >
              <BookOpen className="w-3.5 h-3.5" />
              <span>RAG Knowledge</span>
            </button>
          </nav>

          {/* Right Action: Status & Reset */}
          <div className="flex items-center space-x-2.5 self-end md:self-auto">
            <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-[11px]">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span className="text-zinc-300 font-mono">
                API: {systemHealth ? "ONLINE" : "CONNECTING"}
              </span>
            </div>

            <button
              onClick={onReset}
              disabled={isResetting}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-[11px] font-semibold bg-zinc-900 hover:bg-zinc-800 text-zinc-300 border border-zinc-700/80 transition disabled:opacity-50"
              title="Reset simulated microservices and telemetry metrics to healthy baseline"
            >
              <RefreshCw
                className={`w-3.5 h-3.5 text-zinc-400 ${
                  isResetting ? "animate-spin text-indigo-400" : ""
                }`}
              />
              <span>Reset Env</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
