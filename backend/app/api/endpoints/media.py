from fastapi import APIRouter, UploadFile, File
from typing import Any, cast
import uuid
from app.tasks.media_tasks import process_media_task

router = APIRouter()

@router.post("/upload")
async def upload_media(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    
    # Em produção: enviar o arquivo para um Object Storage (AWS S3 ou MinIO)
    temp_file_path = f"/tmp/{job_id}_{file.filename}"
    with open(temp_file_path, "wb") as f:
        f.write(await file.read())

    # Envia a tarefa para a fila do Celery sem bloquear o FastAPI
    task = cast(Any, process_media_task).delay(temp_file_path, job_id)

    return {
        "job_id": job_id,
        "task_id": task.id,
        "status": "PENDING",
        "message": "Arquivo recebido. Processamento assíncrono iniciado."
    }