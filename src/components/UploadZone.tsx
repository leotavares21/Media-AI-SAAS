"use client";

import { UploadCloud } from "lucide-react";
import { FileUploader } from "@/src/components/FileUploader";

interface UploadZoneProps {
  setJobId: (jobId: string) => void;
  jobId: string | null;
}

export function UploadZone({ setJobId, jobId }: UploadZoneProps) {
  return (
    <div className="w-xl max-w-screen">
      <div className="glow-orb w-96 h-96 top-10 left-10"></div>
      <div className="glow-orb w-96 h-96 bottom-10 right-10"></div>

      <div className="glass-card flex flex-col gap-4 p-6 rounded-2xl">
        <h2 className="font-bold text-xl mb-4">Upload de Mídia</h2>

        <div className="flex flex-col items-center gap-2 border-2 border-dashed text-center border-sky-primary p-10 rounded-2xl">
          <UploadCloud className="w-8 h-8 text-sky-primary" />

          <p className="font-semibold ">
            Arraste seu áudio/vídeo ou clique para navegar
          </p>
          <p className="text-sky-primary">Suporta MP4, MP3, WAV (Até 500MB)</p>
        </div>

        {!jobId ? (
          <FileUploader onUploadSuccess={(id) => setJobId(id)} />
        ) : null}
      </div>
    </div>
  );
}
