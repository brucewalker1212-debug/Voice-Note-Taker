from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.routes.voice_notes import router as voice_notes_router
from app.routes.telegram_bot import router as telegram_router
from .db import start_session, end_session, get_active_session_for_tech, list_projects, save_voice_note

app = FastAPI(title="Voice Notes API")

@app.on_event("startup")
async def startup_event():
    """FastAPI startup event handler"""
    print("🚀 FastAPI server started, waiting for Telegram updates...")
    
    # Get and mask the Telegram bot token
    telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if telegram_token:
        masked_token = telegram_token[:6] + "***" if len(telegram_token) > 6 else "***"
        print(f"TELEGRAM_BOT_TOKEN: {masked_token}")
    else:
        print("TELEGRAM_BOT_TOKEN: Not found in environment variables")

class StartSessionIn(BaseModel):
    project_id: str
    tech_id: str
    session_name: str

class EndSessionIn(BaseModel):
    session_id: str
    status: Optional[str] = "completed"  # 'completed' or 'abandoned'

class SaveNoteIn(BaseModel):
    session_id: str
    tech_id: str
    text: str
    note_type: Optional[str] = "internal"  # contractor|manager|client|internal

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/projects")
def get_projects():
    return {"projects": list_projects()}

@app.get("/sessions/active/{tech_id}")
def get_active(tech_id: str):
    s = get_active_session_for_tech(tech_id)
    return {"session": s}

@app.post("/sessions/start")
def api_start_session(body: StartSessionIn):
    try:
        sess = start_session(body.project_id, body.tech_id, body.session_name)
        return {"session": sess}
    except Exception as e:
        raise HTTPException(400, str(e))

@app.post("/sessions/end")
def api_end_session(body: EndSessionIn):
    try:
        sess = end_session(body.session_id, body.status)
        return {"session": sess}
    except Exception as e:
        raise HTTPException(400, str(e))

@app.post("/voice-notes/save")
def api_save_note(body: SaveNoteIn):
    try:
        note = save_voice_note(body.session_id, body.tech_id, body.text, body.note_type)
        return {"note": note}
    except Exception as e:
        raise HTTPException(400, str(e))

# Mount our feature routes under /api/v1
app.include_router(voice_notes_router, prefix="/api/v1")

# Mount telegram bot routes
app.include_router(telegram_router)
