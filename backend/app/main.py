from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.s3 import ensure_bucket_exists

app = FastAPI()

# Permite que o Next.js se conecte à API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    ensure_bucket_exists()