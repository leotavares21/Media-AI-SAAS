import json
import time
import redis
from app.core.celery_app import celery_app

# Cliente Redis para publicar mensagens no canal Pub/Sub
redis_client = redis.Redis.from_url("redis://localhost:6379/0")

def send_progress(job_id: str, status: str, progress: int, message: str):
    """Publica o estado atual do processamento no canal Pub/Sub do Redis."""
    payload = json.dumps({
        "status": status,
        "progress": progress,
        "message": message
    })
    redis_client.publish(f"job:{job_id}", payload)

@celery_app.task(bind=True)
def process_media_task(self, file_path: str, job_id: str):
    # Inicio do processamento
    send_progress(job_id, "PROCESSING", 10, "Iniciando transcrição com Whisper...")
    time.sleep(3)

    # Etapa intermediária
    send_progress(job_id, "PROCESSING", 60, "Gerando resumo e tópicos com IA...")
    time.sleep(3)

    # Conclusão
    send_progress(job_id, "COMPLETED", 100, "Análise concluída com sucesso!")
    return {"job_id": job_id, "status": "COMPLETED"}