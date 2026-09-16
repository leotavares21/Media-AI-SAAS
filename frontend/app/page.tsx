"use client";

import { UploadZone } from "@/src/components/UploadZone";
import { ProcessingStatus } from "@/src/components/ProcessingStatus";
import { InsightsViewer } from "@/src/components/InsightsViewer";

import { useEffect, useState } from "react";
import { useJobProgress } from "@/src/hooks/useJobProgress";

interface JobResult {
  summary: string;
  transcription: string;
  sentiment?: "Positivo" | "Neutro" | "Negativo";
  topics?: string[];
}

export default function Home() {
  const [jobId, setJobId] = useState<string | null>(null);
  const [result, setResult] = useState<JobResult | null>(null);

  // O hook inicia automaticamente o escuta SSE assim que jobId deixa de ser null
  const { progress, stepMessage, status } = useJobProgress(jobId);

  // Dispara a busca do resultado assim que o SSE informar 'COMPLETED'
  useEffect(() => {
    if (status === "COMPLETED" && jobId) {
      const API_URL =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

      fetch(`${API_URL}/api/v1/jobs/${jobId}`)
        .then((res) => res.json())
        .then((data) => {
          if (data.result) {
            setResult(data.result);
          }
        })
        .catch((err) => console.error("Erro ao buscar resultado:", err));
    }
  }, [status, jobId]);

  return (
    <main className="flex flex-col w-screen gap-6 justify-center items-center min-h-screen">
      <UploadZone setJobId={setJobId} jobId={jobId} />
      {/* SE HOUVER JOB: Oculta o upload e exibe o progresso do SSE */}
      {jobId && (
        <>
          <ProcessingStatus
            progress={progress}
            message={stepMessage}
            status={status}
          />

          {/* Botão de reset ao finalizar */}
          {(status === "COMPLETED" || status === "FAILED") && (
            <button
              onClick={() => setJobId(null)}
              className="mt-4 py-2 px-4 bg-sky-primary hover:bg-sky-hover text-sky-light rounded-lg text-sm font-medium transition-colors"
            >
              Enviar outro arquivo
            </button>
          )}
        </>
      )}

      {status === "COMPLETED" && result && (
        <InsightsViewer
          summary={result.summary}
          transcription={result.transcription}
          sentiment={result.sentiment}
          topics={result.topics}
        />
      )}
    </main>
  );
}
