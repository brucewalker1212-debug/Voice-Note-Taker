import os
import uuid
from fastapi import APIRouter, HTTPException, Request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio
from typing import Dict, Any
import logging
from ..db import start_session, end_session, save_voice_note
from ..supabase_client import supabase

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Get Telegram bot token from environment
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

# Initialize bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Store for user sessions (in production, use a proper database)
user_sessions: Dict[int, Dict[str, Any]] = {}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command - creates a new project"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "Unknown"
    
    try:
        # Create a new project in Supabase
        project_data = {
            "name": f"Project for {username}",
            "description": f"Telegram project for user {username}",
            "created_by": str(user_id)
        }
        
        resp = supabase.table("projects").insert(project_data).execute()
        project = resp.data[0]
        
        # Store user info with project
        user_sessions[user_id] = {
            "user_id": user_id,
            "username": username,
            "project_id": project["id"],
            "session_id": None
        }
        
        await update.message.reply_text(
            f"Hello {username}! Welcome to Voice Notes Bot.\n\n"
            f"Project created: {project['name']}\n"
            "Available commands:\n"
            "/startsession - Start a new session\n"
            "/endsession - End current session"
        )
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        await update.message.reply_text("Error creating project. Please try again.")

async def startsession_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /startsession command - creates a new session"""
    user_id = update.effective_user.id
    
    if user_id not in user_sessions or not user_sessions[user_id].get("project_id"):
        await update.message.reply_text("Please use /start first to create a project.")
        return
    
    try:
        # Create a new session in Supabase
        project_id = user_sessions[user_id]["project_id"]
        session_name = f"Session for {user_sessions[user_id]['username']}"
        
        session = start_session(project_id, str(user_id), session_name)
        
        # Update user session
        user_sessions[user_id]["session_id"] = session["id"]
        
        await update.message.reply_text(
            f"Session started!\n"
            f"Session ID: {session['id']}\n"
            "You can now record voice notes."
        )
    except Exception as e:
        logger.error(f"Error starting session: {e}")
        await update.message.reply_text("Error starting session. Please try again.")

async def endsession_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /endsession command - ends the current session"""
    user_id = update.effective_user.id
    
    if user_id not in user_sessions or not user_sessions[user_id].get("session_id"):
        await update.message.reply_text("No active session found. Use /startsession first.")
        return
    
    try:
        # End the session in Supabase
        session_id = user_sessions[user_id]["session_id"]
        ended_session = end_session(session_id, "completed")
        
        # Clear session from user data
        user_sessions[user_id]["session_id"] = None
        
        await update.message.reply_text(
            f"Session ended successfully!\n"
            f"Session ID: {ended_session['id']}\n"
            f"Status: {ended_session['status']}"
        )
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        await update.message.reply_text("Error ending session. Please try again.")

async def log_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /test command - logs the entire update JSON"""
    import json
    
    # Convert update to dict and print with prefix
    update_dict = update.to_dict()
    print(f"[TELEGRAM UPDATE] {json.dumps(update_dict, indent=2)}")
    
    # Reply to user
    await update.message.reply_text("✅ Update received")

# Create application
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Add command handlers
application.add_handler(CommandHandler("start", start_command))
application.add_handler(CommandHandler("startsession", startsession_command))
application.add_handler(CommandHandler("endsession", endsession_command))
application.add_handler(CommandHandler("test", log_update))

@router.post("/telegram/{token}")
async def telegram_webhook(token: str, request: Request):
    """Handle Telegram webhook updates"""
    if token != TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        # Get the update from the request body
        update_data = await request.json()
        update = Update.de_json(update_data, bot)
        
        # Process the update
        await application.process_update(update)
        
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error processing Telegram update: {e}")
        raise HTTPException(status_code=500, detail="Error processing update")
