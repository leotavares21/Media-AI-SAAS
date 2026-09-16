"use client";

import { UploadCloud } from "lucide-react";
import { useState, useRef, DragEvent } from "react";

export function FileUploader({
  onUploadSuccess,
}: {
  onUploadSuccess?: (jobId: string) => void;
}) {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  // Referência para disparar o clique no input oculto
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Handlers para Drag and Drop
  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (!isUploading) setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (isUploading) return;

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  // Dispara a escolha manual de arquivo
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async (e: React.MouseEvent<HTMLButtonElement>) => {
    // Evita abrir a janela de seleção ao clicar no botão de upload
    e.stopPropagation();

    if (!file) return;

    setIsUploading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/api/v1/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Erro na requisição: ${response.statusText}`);
      }

      const data = await response.json();

      if (onUploadSuccess) {
        onUploadSuccess(data.job_id);
      }
    } catch (error) {
      console.error("Falha ao enviar arquivo:", error);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="glass-card flex flex-col gap-4 p-6 rounded-2xl">
      <div
        onClick={() => !isUploading && fileInputRef.current?.click()}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`flex flex-col gap-4 transition-all rounded-2xl ${
          isDragging
            ? "opacity-70 scale-[0.99] border-2 border-dashed border-sky-primary p-2"
            : ""
        }`}
      >
        <h2 className="font-bold text-xl mb-4">Upload de Mídia</h2>
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileChange}
          accept="audio/*,video/*"
          className="hidden"
        />

        <div className="flex flex-col items-center gap-2 border-2 border-dashed text-center border-sky-primary p-10 rounded-2xl hover:bg-slate-100 cursor-pointer">
          <UploadCloud className="w-8 h-8 text-sky-primary" />

          {!file ? (
            <>
              <p className="font-semibold">
                Arraste seu áudio/vídeo ou clique para navegar
              </p>
              <p className="text-sky-primary">
                Suporta MP4, MP3, WAV (Até 500MB)
              </p>
            </>
          ) : (
            <p className="font-semibold">{file.name}</p>
          )}
        </div>

        <div className="flex justify-between items-center gap-1">
          <label
            htmlFor="fileInput"
            className="py-2 px-6 bg-sky-light w-fit rounded-2xl text-sky-glow hover:bg-foreground hover:text-sky-light font-medium cursor-pointer"
          >
            Escolher arquivo
          </label>

          <span id="file-name" className="text-slate-600 max-w-60 line-clamp-1">
            {!file ? "Nenhum arquivo selecionado" : file.name}
          </span>
        </div>
        <button
          onClick={handleUpload}
          className="w-full px-2 py-4 bg-sky-primary rounded-2xl font-semibold text-sky-light hover:bg-sky-hover disabled:opacity-50 cursor-pointer transition-colors"
        >
          {isUploading ? "Enviando arquivo..." : "Iniciar Processamento"}
        </button>
      </div>
    </div>
  );
}
