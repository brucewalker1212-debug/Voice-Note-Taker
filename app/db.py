from datetime import datetime, timezone
from typing import Any, Dict, Optional
from .supabase_client import supabase

# --- Sessions ---
def start_session(project_id: str, tech_id: str, session_name: str) -> Dict[str, Any]:
    resp = supabase.table("sessions").insert({
        "project_id": project_id,
        "tech_id": tech_id,
        "session_name": session_name
    }).execute()
    return resp.data[0]

def end_session(session_id: str, status: str = "completed") -> Dict[str, Any]:
    resp = supabase.table("sessions").update({"status": status}).eq("id", session_id).execute()
    if not resp.data:
        raise ValueError("Session not found")
    return resp.data[0]

def get_active_session_for_tech(tech_id: str) -> Optional[Dict[str, Any]]:
    resp = (
        supabase.table("sessions")
        .select("*")
        .eq("tech_id", tech_id)
        .eq("status", "active")
        .order("started_at", desc=True)
        .limit(1)
        .execute()
    )
    return resp.data[0] if resp.data else None

# --- Projects ---
def list_projects(limit: int = 100):
    return supabase.table("projects").select("*").order("created_at", desc=True).limit(limit).execute().data

# --- Voice notes ---
def save_voice_note(session_id: str, tech_id: str, text: str, note_type: str = "internal"):
    resp = supabase.table("voice_notes").insert({
        "session_id": session_id,
        "tech_id": tech_id,
        "transcribed_text": text,
        "note_type": note_type,
        "created_at": datetime.now(timezone.utc).isoformat()
    }).execute()
    return resp.data[0]

# --- Reports ---
def create_report(session_id: str, project_id: str, report_text: str, storage_key: str):
    resp = supabase.table("reports").insert({
        "session_id": session_id,
        "project_id": project_id,
        "report_text": report_text,
        "file_path": storage_key
    }).execute()
    return resp.data[0]


