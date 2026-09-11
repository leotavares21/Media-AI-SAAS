"use client";

import { useState } from "react";
import { Sparkles, MessageSquareText, Smile, Tag } from "lucide-react";

interface InsightsProps {
  summary: string;
  transcription: string;
  sentiment: "Positivo" | "Neutro" | "Negativo";
  topics: string[];
}

export function InsightsViewer({
  summary,
  transcription,
  sentiment,
  topics,
}: InsightsProps) {
  const [activeTab, setActiveTab] = useState<"summary" | "transcript">(
    "summary",
  );

  const sentimentColor = {
    Positivo: "bg-emerald-600/10 text-emerald-500 border-emerald-600/20",
    Neutro: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    Negativo: "bg-rose-500/10 text-rose-400 border-rose-500/20",
  }[sentiment];

  return (
    <div className="glass-card rounded-xl p-6 text-slate-100 max-w-3xl mx-auto space-y-6">
      {/* Badges de Destaques / Metadados */}
      <div className="flex flex-wrap items-center gap-3 pb-4 border-b border-sky-light">
        <div
          className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs border ${sentimentColor}`}
        >
          <Smile className="w-4 h-4" />
          <span>Sentimento: {sentiment}</span>
        </div>

        <div className="flex items-center gap-1.5 text-xs text-slate-400">
          <Tag className="w-4 h-4" />
          <span>Tópicos:</span>
          {topics.map((topic, i) => (
            <span
              key={i}
              className="bg-foreground px-2 py-0.5 rounded text-sky-light"
            >
              {topic}
            </span>
          ))}
        </div>
      </div>

      {/* Navegação entre Abas */}
      <div className="flex border-b border-sky-light gap-4">
        <button
          onClick={() => setActiveTab("summary")}
          className={`pb-2 text-sm font-medium flex items-center gap-2 border-b-2 transition-colors ${
            activeTab === "summary"
              ? "border-sky-primary text-sky-primary"
              : "border-transparent text-slate-400 hover:text-sky-hover"
          }`}
        >
          <Sparkles className="w-4 h-4" />
          Resumo Inteligente
        </button>
        <button
          onClick={() => setActiveTab("transcript")}
          className={`pb-2 text-sm font-medium flex items-center gap-2 border-b-2 transition-colors ${
            activeTab === "transcript"
              ? "border-sky-primary text-sky-primary"
              : "border-transparent text-slate-400 hover:text-sky-hover"
          }`}
        >
          <MessageSquareText className="w-4 h-4" />
          Transcrição Completa
        </button>
      </div>

      {/* Conteúdo */}
      <div className="text-foreground leading-relaxed text-sm">
        {activeTab === "summary" ? (
          <div className="bg-sky-light p-4 rounded-lg">{summary}</div>
        ) : (
          <div className="bg-sky-light p-4 rounded-lg whitespace-pre-wrap max-h-96 overflow-y-auto">
            {transcription}
          </div>
        )}
      </div>
    </div>
  );
}
