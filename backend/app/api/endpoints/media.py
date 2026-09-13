# app/api/endpoints/media.py
from fastapi import APIRouter, UploadFile, HTTPException, File
from typing import Any, cast
import uuid
from app.core.s3 import upload_file_to_s3
from app.tasks.media_tasks import process_media_task
from celery.result import AsyncResult
from app.core.celery_app import celery_app

router = APIRouter()

@router.post("/upload")
async def upload_media(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    filename = file.filename or "upload"
    extension = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
    s3_key = f"raw/{job_id}.{extension}"

    # Envia o stream do arquivo direto para o MinIO sem salvar no disco do FastAPI
    upload_file_to_s3(file.file, s3_key, file.content_type or "application/octet-stream")

    # Dispara a task no Celery passando apenas a referência da chave no S3
    task = cast(Any, process_media_task).delay(s3_key=s3_key, job_id=job_id)

    return {
        "job_id": job_id,
        "task_id": task.id,
        "s3_key": s3_key,
        "status": "PENDING"
    }

@router.get("/api/v1/jobs/{job_id}")
async def get_job_result(job_id: str):
    """Retorna os dados processados (transcrição, resumo) de um job concluído."""
    task_result = AsyncResult(job_id, app=celery_app)

    # Se a tarefa ainda não terminou
    if not task_result.ready():
        return {
            "job_id": job_id,
            "status": task_result.status,
            "result": None
        }

    # Se a tarefa falhou durante a execução no Celery
    if task_result.failed():
        raise HTTPException(
            status_code=500, 
            detail=f"Erro no processamento: {str(task_result.info)}"
        )

    # Retorna o dicionário com transcription, summary, etc., devolvido pela task
    return {
        "job_id": job_id,
        "status": "COMPLETED",
        "result": task_result.result
    }