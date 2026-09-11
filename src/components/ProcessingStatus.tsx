"use client";

import { Loader2, CheckCircle2, AlertCircle } from "lucide-react";

interface ProcessingStatusProps {
  progress: number;
  message: string;
  status: "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED";
}

export function ProcessingStatus({
  progress,
  message,
  status,
}: ProcessingStatusProps) {
  return (
    <div className="glass-card p-6 rounded-xl max-w-xl mx-auto text-sky-glow">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          {status === "PROCESSING" && (
            <Loader2 className="w-5 h-5 animate-spin text-sky-primary" />
          )}
          {status === "COMPLETED" && (
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          )}
          {status === "FAILED" && (
            <AlertCircle className="w-5 h-5 text-red-400" />
          )}
          <span className="font-semibold text-sm">{message}</span>
        </div>
        <span className="text-sm font-mono text-sky-primary">{progress}%</span>
      </div>

      <div className="w-full bg-sky-light h-2.5 rounded-full overflow-hidden">
        <div
          className="bg-sky-primary h-full transition-all duration-300 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
}
