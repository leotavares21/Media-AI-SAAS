import os
import json
import redis
import whisper
import tempfile
from app.core.celery_app import celery_app
from app.core.s3 import download_file_from_s3
from app.core.database import SessionLocal
from app.models.job import Job, JobStatus
from openai import OpenAI
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env para o sistema
load_dotenv()

# Cliente Redis para emissão de eventos em tempo real
redis_client = redis.Redis.from_url("redis://localhost:6379/0")

# Carrega o modelo do Whisper na inicialização do Worker
whisper_model = whisper.load_model("base")

# Obtém a pasta temporária do sistema operacional de forma cross-platform
TEMP_DIR = tempfile.gettempdir()

def generate_ai_insights(transcription_text: str) -> dict:
    """Envia a transcrição para a API da Groq e retorna resumo, sentimento e tópicos."""
    if not transcription_text or not transcription_text.strip():
        return {
            "summary": "Nenhum áudio ou fala detectado para resumir.",
            "sentiment": "Neutro",
            "topics": []
        }

    # Conecta à API da Groq utilizando a SDK da OpenAI
    client = OpenAI(
         base_url="https://api.groq.com/openai/v1",
         api_key=os.environ.get("GROQ_API_KEY")
    )

    prompt = f"""
    Analise o texto transcrito abaixo e extraia as seguintes informações:
    1. "summary": Um resumo claro de 2 a 3 frases.
    2. "sentiment": Escolha estritamente UM entre ["Positivo", "Negativo", "Neutro"].
    3. "topics": Uma lista com 2 a 5 palavras-chave/temas abordados.

    Responda EXCLUSIVAMENTE em formato JSON estrito, sem formatação markdown extra:
    {{
      "summary": "Texto do resumo...",
      "sentiment": "Sentimento...",
      "topics": ["Tópico 1", "Tópico 2"]
    }}

    Transcrição:
    "{transcription_text}"
    """

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",  # Modelo rápido e gratuito na Groq
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("A API retornou uma resposta vazia.")
        data = json.loads(content)

        return {
            "summary": data.get("summary", "Resumo não disponível."),
            "sentiment": data.get("sentiment", "Neutro"),
            "topics": data.get("topics", [])
        }

    except Exception as e:
        print(f"[ERRO GROQ AI SERVICE]: {e}")
        return {
            "summary": (
                transcription_text[:300] + "..."
                if len(transcription_text) > 300
                else transcription_text
            ),
            "sentiment": "Neutro",
            "topics": ["Geral"]
        }


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

        # Notificação de progresso
        notify_progress(job_id, "PROCESSING", 80, "Gerando resumo e tópicos com IA...")

        # Chamada dinâmica real usando o texto transcrito do Whisper
        ai_insights = generate_ai_insights(transcription_text)

        summary_text = ai_insights["summary"]
        sentiment = ai_insights["sentiment"]
        topics = ai_insights["topics"]

        # Estrutura final enviada para o frontend e banco de dados
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
            job.sentiment = sentiment
            job.topics = topics
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