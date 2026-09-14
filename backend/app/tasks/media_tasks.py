import os
import json
import redis
import whisper
import tempfile
from app.core.celery_app import celery_app
from app.core.s3 import download_file_from_s3
from app.core.database import SessionLocal
from app.models.job import Job, JobStatus

# Cliente Redis para emissão de eventos em tempo real
redis_client = redis.Redis.from_url("redis://localhost:6379/0")

# Carrega o modelo do Whisper na inicialização do Worker
whisper_model = whisper.load_model("base")

# Obtém a pasta temporária do sistema operacional de forma cross-platform
TEMP_DIR = tempfile.gettempdir()

def notify_progress(job_id: str, status: str, progress: int, message: str):
    """Publica atualizações no canal Pub/Sub do Redis para o SSE."""
    payload = json.dumps({
        "status": status,
        "progress": progress,
        "message": message
    })
    redis_client.publish(f"job:{job_id}", payload)


@celery_app.task(bind=True)
def process_media_task(self, s3_key: str, job_id: str):
    # Gera o caminho correto usando os.path.join (funciona no Windows e Linux)
    file_name = f"{job_id}_{os.path.basename(s3_key)}"
    local_path = os.path.join(TEMP_DIR, file_name)

    db = SessionLocal()

    try:
        # Garante que o diretório exista antes do download
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        # 1. Notifica início e atualiza banco
        notify_progress(job_id, "PROCESSING", 10, "Baixando mídia do MinIO...")
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = JobStatus.PROCESSING
            job.progress = 10
            db.commit()

        # Baixa o arquivo do MinIO para o disco temporário do worker
        download_file_from_s3(s3_key, local_path)

        # 2. Transcrição com Whisper
        notify_progress(job_id, "PROCESSING", 40, "Transcrevendo áudio com Whisper...")
        transcription_result = whisper_model.transcribe(local_path)
        transcription_value = transcription_result.get("text", "")
        transcription_text = (
            transcription_value.strip()
            if isinstance(transcription_value, str)
            else " ".join(str(item) for item in transcription_value).strip()
        )

        # 3. Geração de Resumo e Metadados (Pode ser integrado com OpenAI/LLM)
        notify_progress(job_id, "PROCESSING", 80, "Gerando resumo e tópicos com IA...")
        summary_text = (
            transcription_text[:300] + "..."
            if len(transcription_text) > 300
            else transcription_text
        )
        sentiment = "Positivo"  # "Positivo" | "Neutro" | "Negativo"
        topics = ["Tecnologia", "Análise de Mídia", "Transcrição"]

        # Estrutura final enviada para o frontend
        result_payload = {
            "job_id": job_id,
            "transcription": transcription_text,
            "summary": summary_text,
            "sentiment": sentiment,
            "topics": topics
        }

        # 4. Salva o resultado final no PostgreSQL
        if job:
            job.status = JobStatus.COMPLETED
            job.progress = 100
            job.transcription = transcription_text
            job.summary = summary_text
            db.commit()

        notify_progress(job_id, "COMPLETED", 100, "Processamento concluído com sucesso!")
        return result_payload

    except Exception as e:
        db.rollback()
        # Notifica falha via SSE e atualiza status de erro no PostgreSQL
        notify_progress(job_id, "FAILED", 0, f"Erro: {str(e)}")
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            db.commit()
        raise e

    finally:
        # 5. Garante a limpeza do arquivo local e fechamento da sessão DB
        if os.path.exists(local_path):
            os.remove(local_path)
        db.close()