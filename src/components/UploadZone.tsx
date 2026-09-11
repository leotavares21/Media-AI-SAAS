"use client";

import { UploadCloud } from "lucide-react";

export function UploadZone() {
  return (
    <div className="flex items-center justify-center h-screen">
      <div className="glow-orb w-96 h-96 top-10 left-10"></div>
      <div className="glow-orb w-96 h-96 bottom-10 right-10"></div>

      <div className="glass-card flex flex-col gap-4 p-6 rounded-2xl">
        <h2 className="font-bold text-xl mb-4">Upload de Mídia</h2>

        <div className="flex flex-col items-center gap-2 border-2 border-dashed border-sky-primary p-10 rounded-2xl">
          
          <UploadCloud className="w-8 h-8 text-sky-primary" />

          <p className="font-semibold ">
            Arraste seu áudio/vídeo ou clique para navegar
          </p>
          <p className="text-sky-primary">Suporta MP4, MP3, WAV (Até 500MB)</p>
        </div>

        <label
          htmlFor="fileID"
          className="py-2 px-6 bg-sky-light w-fit rounded-lg text-sky-glow hover:bg-foreground hover:text-sky-light font-medium cursor-pointer"
        >
          Escolher arquivo
        </label>

        <span id="file-name" className="text-slate-600">
          Nenhum arquivo selecionado
        </span>
        
        <input type="file" id="fileID" className="hidden" />

        <button className="py-4 bg-sky-primary rounded-2xl font-semibold text-sky-light hover:bg-sky-hover cursor-pointer">
          Iniciar Processamento por IA
        </button>
      </div>
    </div>
  );
}
