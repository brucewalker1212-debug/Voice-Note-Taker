from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
import uuid
from datetime import datetime, timezone
from app.services.transcribe import transcribe_bytes

router = APIRouter()

class CreateSessionRequest(BaseModel):
    user_id: str

class CreateSessionResponse(BaseModel):
    session_id: str
    created_at: str

@router.post("/sessions", response_model=CreateSessionResponse)
def create_session(payload: CreateSessionRequest):
    sid = str(uuid.uuid4())
    return {"session_id": sid, "created_at": datetime.now(timezone.utc).isoformat()}

@router.post("/voice-notes")
async def upload_voice_note(
    session_id: str = Form(...),
    file: UploadFile = File(...)
):
    if not session_id:
        raise HTTPException(400, "session_id required")
    data = await file.read()
    transcript = transcribe_bytes(data)  # no audio storage
    return {
        "note_id": str(uuid.uuid4()),
        "session_id": session_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": len(data),
        "transcript": transcript
    }

