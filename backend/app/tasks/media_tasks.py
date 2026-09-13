import os
from app.core.celery_app import celery_app
from app.core.s3 import download_file_from_s3

@celery_app.task(bind=True)
def process_media_task(self, s3_key: str, job_id: str):
    local_path = f"/tmp/{job_id}_{os.path.basename(s3_key)}"
    
    # 1. Baixa a mídia do MinIO
    download_file_from_s3(s3_key, local_path)
    
    try:
        # 2. Executa transcrição / IA usando local_path
        # whisper_model.transcribe(local_path)
        pass
    finally:
        # 3. Remove o arquivo temporário local do worker
        if os.path.exists(local_path):
            os.remove(local_path)