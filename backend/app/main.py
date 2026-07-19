from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI

# Load variables from .env (e.g. PORT, APP_ENV) into the environment
load_dotenv()

app = FastAPI(
    title="Task Tracker API",
    description="Module 1 Task Tracker REST API",
    version="0.1.0",
)


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    """Basic liveness check for the API."""
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
