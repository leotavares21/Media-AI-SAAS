"use client";

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

      {!jobId ? <FileUploader onUploadSuccess={(id) => setJobId(id)} /> : null}
    </div>
  );
}
