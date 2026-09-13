import os
import boto3
from botocore.exceptions import ClientError

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadminpassword")
BUCKET_NAME = os.getenv("MINIO_BUCKET", "media-files")

def get_s3_client():
    """Retorna uma instância configurada do cliente S3 para o MinIO."""
    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        region_name="us-east-1"
    )

def ensure_bucket_exists():
    """Garante que o bucket padrão exista ao iniciar a aplicação."""
    s3 = get_s3_client()
    try:
        s3.head_bucket(Bucket=BUCKET_NAME)
    except ClientError:
        s3.create_bucket(Bucket=BUCKET_NAME)

def upload_file_to_s3(file_obj, object_name: str, content_type: str) -> str:
    """Faz o upload direto do buffer de memória para o MinIO."""
    s3 = get_s3_client()
    s3.upload_fileobj(
        file_obj,
        BUCKET_NAME,
        object_name,
        ExtraArgs={"ContentType": content_type}
    )
    return object_name

def download_file_from_s3(object_name: str, destination_path: str):
    """Baixa o arquivo do MinIO para o disco local do worker Celery."""
    s3 = get_s3_client()
    s3.download_file(BUCKET_NAME, object_name, destination_path)