# Voice Notes API

## Setup

Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the API

```bash
uvicorn app.main:app --reload --port 8000
```

## Testing

Set environment variables (Windows):
```cmd
set TEST_PROJECT_ID=<uuid>
set TEST_TECH_ID=<uuid>
```

Run the sanity test:
```bash
python scripts/sanity_test.py
```

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_SERVICE_KEY` - Your Supabase service role key
- `OPENAI_API_KEY` - Your OpenAI API key for transcription
- `TEST_PROJECT_ID` - Optional, for testing
- `TEST_TECH_ID` - Optional, for testing
