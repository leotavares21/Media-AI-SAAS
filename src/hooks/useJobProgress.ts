"use client";

import { useEffect, useState } from "react";

interface JobProgress {
  status: "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED";
  progress: number; // 0 a 100
  stepMessage: string;
}

export function useJobProgress(jobId: string | null) {
  const [jobData, setJobData] = useState<JobProgress>({
    status: "PENDING",
    progress: 0,
    stepMessage: "Aguardando envio...",
  });

  useEffect(() => {
    if (!jobId) return;

    // Conecta ao endpoint de SSE do seu backend Python (FastAPI)
    const eventSource = new EventSource(
      `http://localhost:8000/api/v1/jobs/${jobId}/stream`,
    );

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setJobData({
        status: data.status,
        progress: data.progress,
        stepMessage: data.message,
      });

      if (data.status === "COMPLETED" || data.status === "FAILED") {
        eventSource.close();
      }
    };

    eventSource.onerror = (err) => {
      console.error("Erro na conexão SSE:", err);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [jobId]);

  return jobData;
}
