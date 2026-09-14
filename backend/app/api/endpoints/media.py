import uuid
import asyncio
import redis.asyncio as aioredis
from typing import Any, cast
from fastapi import APIRouter, UploadFile, HTTPException, File, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from celery.result import AsyncResult

from app.core.s3 import upload_file_to_s3
from app.core.celery_app import celery_app
from app.core.database import get_db
from app.models.job import Job, JobStatus
from app.tasks.media_tasks import process_media_task

# Padroniza o prefixo /api/v1 para todas as rotas deste módulo
router = APIRouter(prefix="/api/v1")

@router.post("/upload")
async def upload_media(file: UploadFile = File(...), db: Session = Depends(get_db)):
    job_id = str(uuid.uuid4())
    filename = file.filename or "upload"
    extension = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
    s3_key = f"raw/{job_id}.{extension}"
    file_size = f"{(file.size / (1024 * 1024)):.1f} MB" if file.size else "N/A"

    # 1. Envia o stream para o MinIO
    upload_file_to_s3(file.file, s3_key, file.content_type or "application/octet-stream")

    # 2. Persiste o registro inicial no PostgreSQL
    db_job = Job(
        id=job_id,
        filename=filename,
        file_size=file_size,
        s3_key=s3_key,
        status=JobStatus.PENDING,
        progress=0
    )
    db.add(db_job)
    db.commit()

    # 3. Dispara a task no Celery
    task = cast(Any, process_media_task).apply_async(
        kwargs={"s3_key": s3_key, "job_id": job_id},
        task_id=job_id
    )

    return {
        "job_id": job_id,
        "task_id": task.id,
        "s3_key": s3_key,
        "status": "PENDING"
    }

@router.get("/jobs/{job_id}/stream")
async def stream_job_progress(job_id: str):
    """Canal SSE que envia atualizações de progresso do Redis para o Frontend."""
    async def event_generator():
        redis_async = aioredis.from_url("redis://localhost:6379/0")
        pubsub = redis_async.pubsub()
        await pubsub.subscribe(f"job:{job_id}")

        try:
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    data = message["data"].decode("utf-8")
                    yield f"data: {data}\n\n"
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            await pubsub.unsubscribe(f"job:{job_id}")
            await redis_async.close()

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/jobs/{job_id}")
async def get_job_result(job_id: str, db: Session = Depends(get_db)):
    """Retorna os dados processados (transcrição, resumo) armazenados no PostgreSQL."""
    
    # 1. Busca o registro no banco de dados
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado")

    # 2. Se ainda estiver processando
    if job.status != JobStatus.COMPLETED:
        return {
            "job_id": job_id,
            "status": job.status,
            "result": None
        }

    # 3. Retorna o resultado salvo pelo worker
    return {
        "job_id": job_id,
        "status": "COMPLETED",
        "result": {
            "transcription": job.transcription,
            "summary": job.summary,
            "sentiment": "Positivo",  # Ou buscar do campo se adicionou no Model
            "topics": ["Tecnologia", "Análise de Mídia"]
        }
    }