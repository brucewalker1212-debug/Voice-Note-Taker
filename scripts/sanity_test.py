import requests, os, sys, time

BASE = os.environ.get("BASE_URL", "http://127.0.0.1:8000")
PROJECT_ID = os.environ.get("TEST_PROJECT_ID")  # set these env vars for test
TECH_ID    = os.environ.get("TEST_TECH_ID")

if not PROJECT_ID or not TECH_ID:
    print("Set TEST_PROJECT_ID and TEST_TECH_ID env vars before running.")
    sys.exit(1)

print("Health:", requests.get(f"{BASE}/healthz").json())

# Start session
sess = requests.post(f"{BASE}/sessions/start", json={
    "project_id": PROJECT_ID,
    "tech_id": TECH_ID,
    "session_name": "Field visit - panel A"
}).json()["session"]
print("Started:", sess["id"], sess["status"])

# Simulate Whisper completion
note = requests.post(f"{BASE}/voice-notes/save", json={
    "session_id": sess["id"],
    "tech_id": TECH_ID,
    "text": "Breaker 12 was tripped. Reset and labeled.",
    "note_type": "internal"
}).json()["note"]
print("Saved note:", note["id"])

time.sleep(1)

# End session
ended = requests.post(f"{BASE}/sessions/end", json={
    "session_id": sess["id"],
    "status": "completed"
}).json()["session"]
print("Ended:", ended["status"], "duration:", ended.get("duration_minutes"))
