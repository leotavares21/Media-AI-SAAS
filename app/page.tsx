import { UploadZone } from "@/src/components/UploadZone";
import { ProcessingStatus } from "@/src/components/ProcessingStatus";
import { InsightsViewer } from "@/src/components/InsightsViewer";

export default function Home() {
  return (
    <main>
      <UploadZone />
      <ProcessingStatus
        progress={50}
        message="Processando áudio..."
        status="PROCESSING"
      />
      <InsightsViewer
        summary="Este é um resumo do conteúdo do áudio/vídeo processado."
        transcription="Esta é a transcrição completa do áudio/vídeo processado."
        sentiment="Positivo"
        topics={["Tecnologia", "Inteligência Artificial", "Desenvolvimento"]}
      />
    </main>
  );
}
