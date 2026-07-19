# Task Tracker API

Module 1 of the Task Tracker project: a minimal FastAPI backend skeleton.

This stage only includes application bootstrap and a health check endpoint.
Persistence (JSON file storage, per ADR-001), CRUD endpoints, and the frontend
are added in later modules.

## Tech Stack

- Python 3.11+
- FastAPI
- Pydantic
- Uvicorn (ASGI server)
- python-dotenv (environment variable loading)

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py       # FastAPI app instance + /health endpoint
│   └── data/          # Reserved for tasks.json (future ADR-001 persistence)
├── tests/
│   ├── __init__.py
│   └── test_health.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Setup

1. Create and activate a virtual environment:

   **Linux/macOS:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

   **Windows (PowerShell):**
   ```powershell
   python -m venv venv
   venv\Scripts\Activate.ps1
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy the example environment file and adjust if needed:

   **Linux/macOS:**
   ```bash
   cp .env.example .env
   ```

   **Windows (PowerShell):**
   ```powershell
   Copy-Item .env.example .env
   ```

## Running the Server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

## Testing the Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": "2026-07-19T12:34:56.789012+00:00"
}
```

## Running Tests

```bash
pytest -v
```

## API Documentation

FastAPI generates interactive Swagger docs automatically. With the server
running, open:

```
http://localhost:8000/docs
```
