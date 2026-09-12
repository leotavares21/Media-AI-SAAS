import json
import asyncio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import redis.asyncio as aioredis

router = APIRouter()

REDIS_URL = "redis://localhost:6379/0"

@router.get("/api/v1/jobs/{job_id}/stream")
async def stream_job_progress(job_id: str):
    """Endpoint SSE que faz streaming do progresso do job via Redis Pub/Sub."""
    
    async def event_generator():
        # Conexão assíncrona ao Redis
        client = aioredis.from_url(REDIS_URL)
        pubsub = client.pubsub()
        await pubsub.subscribe(f"job:{job_id}")

        try:
            while True:
                # Ouve mensagens sem bloquear a API
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                
                if message and message["type"] == "message":
                    data = message["data"].decode("utf-8")
                    
                    # Formato padrão exigido pelo Server-Sent Events
                    yield f"data: {data}\n\n"

                    # Se a tarefa foi concluída ou falhou, encerra o streaming
                    parsed_data = json.loads(data)
                    if parsed_data.get("status") in ["COMPLETED", "FAILED"]:
                        break

                await asyncio.sleep(0.2)
        finally:
            await pubsub.unsubscribe(f"job:{job_id}")
            await client.aclose()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Evita cache caso utilize Nginx
        }
    )