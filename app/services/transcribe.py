from openai import OpenAI
import tempfile, os

_client = None
def client():
    global _client
    if _client is None:
        _client = OpenAI()
    return _client

def transcribe_bytes(data: bytes, model: str = "whisper-1") -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as tmp:
        tmp.write(data)
        tmp_path = tmp.name
    try:
        with open(tmp_path, "rb") as f:
            resp = client().audio.transcriptions.create(model=model, file=f)
        return resp.text
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
