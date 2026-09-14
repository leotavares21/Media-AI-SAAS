"use client";

import { useState } from "react";

export function FileUploader({
  onUploadSuccess,
}: {
  onUploadSuccess?: (jobId: string) => void;
}) {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);

    // 1. Cria o formulário em memória
    const formData = new FormData();
    // A chave "file" deve ser idêntica ao parâmetro no FastAPI: file: UploadFile = File(...)
    formData.append("file", file);

    try {
      // 2. Envia para o backend FastAPI
      const response = await fetch("http://localhost:8000/api/v1/upload", {
        method: "POST",
        body: formData,
        /* 
          ⚠️ IMPORTANTE: NÃO defina 'Content-Type': 'multipart/form-data' aqui!
          O navegador precisa definir o header automaticamente junto com o 'boundary' correto.
        */
      });

      if (!response.ok) {
        throw new Error(`Erro na requisição: ${response.statusText}`);
      }

      const data = await response.json();

      // 3. Notifica o componente pai sobre o job_id gerado
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
    <div className="flex flex-col gap-4">
      <input
        type="file"
        onChange={handleFileChange}
        accept="audio/*,video/*"
        className="hidden"
        id="fileInput"
      />
      <div className="flex justify-between items-center">
        <label
          htmlFor="fileInput"
          className="py-2 px-6 bg-sky-light w-fit rounded-2xl text-sky-glow hover:bg-foreground hover:text-sky-light font-medium cursor-pointer"
        >
          Escolher arquivo
        </label>

        <span id="file-name" className="text-slate-600 float-left">
          {!file ? "Nenhum arquivo selecionado" : file.name}
        </span>
      </div>
      <button
        onClick={handleUpload}
        disabled={!file || isUploading}
        className="w-full px-2 py-4 bg-sky-primary rounded-2xl font-semibold text-sky-light hover:bg-sky-hover"
      >
        {isUploading ? "Enviando arquivo..." : "Iniciar Processamento"}
      </button>
    </div>
  );
}
