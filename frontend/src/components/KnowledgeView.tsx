"use client";

import React, { useState } from "react";
import { Runbook, PastIncident } from "../lib/types";
import { BookOpen, Search, Sparkles, FileText, CheckCircle2, AlertTriangle, ExternalLink } from "lucide-react";

interface KnowledgeViewProps {
  runbooks: Runbook[];
  pastIncidents: PastIncident[];
  onSearch: (query: string) => Promise<any>;
}

export function KnowledgeView({ runbooks, pastIncidents, onSearch }: KnowledgeViewProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any | null>(null);
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      setSearchResults(null);
      return;
    }
    setIsSearching(true);
    try {
      const res = await onSearch(searchQuery);
      setSearchResults(res);
    } finally {
      setIsSearching(false);
    }
  };

  const displayedRunbooks = searchResults?.runbooks || runbooks;
  const displayedPast = searchResults?.past_incidents || pastIncidents;

  return (
    <div className="space-y-6">
      {/* Search Header */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-zinc-900 via-zinc-900 to-indigo-950/40 border border-zinc-800">
        <div className="flex items-center space-x-3 mb-2">
          <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <BookOpen className="w-5 h-5" />
          </div>
          <h2 className="text-lg font-bold text-white tracking-tight">RAG Operational Knowledge Base</h2>
        </div>
        <p className="text-xs sm:text-sm text-zinc-400 max-w-3xl leading-relaxed mb-4">
          Authoritative operational runbooks, failure mitigation procedures, and historical incident postmortems queried
          by the AI agent during root cause analysis.
        </p>

        <form onSubmit={handleSearch} className="flex gap-2 max-w-2xl">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-zinc-500 absolute left-3.5 top-3" />
            <input
              type="text"
              placeholder="Search runbooks by symptom (e.g. 'connection pool exhausted', 'OOM', '503 timeout')..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-zinc-950 border border-zinc-800 text-xs sm:text-sm text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-indigo-500"
            />
          </div>
          <button
            type="submit"
            disabled={isSearching}
            className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition flex items-center space-x-2 shrink-0"
          >
            <Sparkles className={`w-3.5 h-3.5 ${isSearching ? "animate-spin" : ""}`} />
            <span>{isSearching ? "Searching..." : "RAG Search"}</span>
          </button>
        </form>
      </div>

      {/* Runbooks Section */}
      <div>
        <h3 className="text-sm font-semibold text-zinc-200 uppercase font-mono tracking-wider mb-4 flex items-center space-x-2">
          <FileText className="w-4 h-4 text-indigo-400" />
          <span>Operational Runbooks ({displayedRunbooks.length})</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {displayedRunbooks.map((rb: any) => (
            <div
              key={rb.id}
              className="p-5 rounded-2xl bg-zinc-900/80 border border-zinc-800 flex flex-col justify-between shadow-lg"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                    {rb.service}
                  </span>
                  {rb.relevance_score && (
                    <span className="text-[11px] font-mono text-emerald-400 font-semibold">
                      Score: {rb.relevance_score}
                    </span>
                  )}
                </div>

                <h4 className="text-base font-bold text-white mb-2">{rb.title}</h4>

                {rb.trigger_patterns && (
                  <div className="mb-3">
                    <span className="text-[10px] font-mono text-zinc-500 uppercase block mb-1">Trigger Signals:</span>
                    <div className="flex flex-wrap gap-1">
                      {rb.trigger_patterns.map((t: string, idx: number) => (
                        <span
                          key={idx}
                          className="px-1.5 py-0.5 rounded bg-zinc-800 text-[10px] font-mono text-zinc-400"
                        >
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {rb.remediation_actions && (
                  <div className="mb-3">
                    <span className="text-[10px] font-mono text-zinc-500 uppercase block mb-1">
                      Standard Remediation:
                    </span>
                    <ul className="space-y-1 text-xs text-zinc-300">
                      {rb.remediation_actions.map((act: string, idx: number) => (
                        <li key={idx} className="flex items-start space-x-1.5">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                          <span>{act}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {rb.content_preview && (
                <p className="mt-3 text-[11px] text-zinc-500 border-t border-zinc-800/80 pt-2 italic">
                  {rb.content_preview}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Historical Incidents & Postmortems */}
      <div>
        <h3 className="text-sm font-semibold text-zinc-200 uppercase font-mono tracking-wider mb-4 flex items-center space-x-2">
          <BookOpen className="w-4 h-4 text-emerald-400" />
          <span>Historical Postmortems ({displayedPast.length})</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {displayedPast.map((pi: any) => (
            <div key={pi.id} className="p-5 rounded-2xl bg-zinc-900/80 border border-zinc-800 shadow-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono font-bold text-white">{pi.title}</span>
                <span className="text-[10px] font-mono text-zinc-500 uppercase">{pi.service}</span>
              </div>
              <div className="space-y-2 text-xs mt-3">
                <div className="p-2.5 rounded-lg bg-zinc-950 border border-zinc-800/80">
                  <span className="text-zinc-500 font-mono uppercase text-[10px] block mb-0.5">Root Cause:</span>
                  <p className="text-zinc-300">{pi.root_cause}</p>
                </div>
                <div className="p-2.5 rounded-lg bg-zinc-950 border border-zinc-800/80">
                  <span className="text-zinc-500 font-mono uppercase text-[10px] block mb-0.5">Resolution:</span>
                  <p className="text-emerald-300">{pi.resolution}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
