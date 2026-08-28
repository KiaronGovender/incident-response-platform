"use client";

import React from "react";
import {
  ShieldAlert,
  Activity,
  Cpu,
  BookOpen,
  RefreshCw,
  Zap,
  Server,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react";

interface NavbarProps {
  activeTab: "incidents" | "simulator" | "telemetry" | "knowledge";
  setActiveTab: (tab: "incidents" | "simulator" | "telemetry" | "knowledge") => void;
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
    <header className="border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Platform Name */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-violet-600 to-rose-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg tracking-tight text-white">
                  AUTONOMOUS INCIDENT RESPONSE
                </span>
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  AI Agent SRE
                </span>
              </div>
              <p className="text-xs text-zinc-400 font-mono">
                Autonomous Root Cause Analysis & Controlled Remediation
              </p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex items-center space-x-1 bg-zinc-900/90 border border-zinc-800 p-1 rounded-xl">
            <button
              onClick={() => setActiveTab("incidents")}
              className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeTab === "incidents"
                  ? "bg-indigo-600 text-white shadow-sm"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50"
              }`}
            >
              <ShieldAlert className="w-4 h-4" />
              <span>Incident Control</span>
            </button>
            <button
              onClick={() => setActiveTab("simulator")}
              className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeTab === "simulator"
                  ? "bg-indigo-600 text-white shadow-sm"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50"
              }`}
            >
              <Cpu className="w-4 h-4" />
              <span>Failure Simulator</span>
            </button>
            <button
              onClick={() => setActiveTab("telemetry")}
              className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeTab === "telemetry"
                  ? "bg-indigo-600 text-white shadow-sm"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50"
              }`}
            >
              <Activity className="w-4 h-4" />
              <span>Observability</span>
            </button>
            <button
              onClick={() => setActiveTab("knowledge")}
              className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
                activeTab === "knowledge"
                  ? "bg-indigo-600 text-white shadow-sm"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50"
              }`}
            >
              <BookOpen className="w-4 h-4" />
              <span>RAG Knowledge</span>
            </button>
          </nav>

          {/* System Health & Reset Action */}
          <div className="flex items-center space-x-3">
            <div className="hidden sm:flex items-center space-x-2 px-3 py-1 rounded-lg bg-zinc-900 border border-zinc-800 text-xs">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span className="text-zinc-300 font-mono">Backend: {systemHealth ? "ONLINE" : "CONNECTING"}</span>
            </div>

            <button
              onClick={onReset}
              disabled={isResetting}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-zinc-800/80 hover:bg-zinc-700 text-zinc-200 border border-zinc-700 transition"
              title="Reset all simulation metrics and services to baseline healthy state"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isResetting ? "animate-spin" : ""}`} />
              <span>Reset Env</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
