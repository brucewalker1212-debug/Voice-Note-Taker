from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.routes.voice_notes import router as voice_notes_router

app = FastAPI(title="Voice Notes API")

@app.get("/health")
def health():
    return {"status": "ok"}

# Mount our feature routes under /api/v1
app.include_router(voice_notes_router, prefix="/api/v1")
