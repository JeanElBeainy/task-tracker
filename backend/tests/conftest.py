import pytest
from fastapi.testclient import TestClient

from app.main import app
from app import storage


@pytest.fixture(autouse=True)
def _reset_storage():
    """Reset in-memory storage before and after each test."""
    storage._reset()
    yield
    storage._reset()


@pytest.fixture
def client() -> TestClient:
    """Return a synchronous TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def created_task(client: TestClient) -> dict:
    """Create a task via POST /tasks and return its JSON body."""
    r = client.post("/tasks", json={"title": "fixture task"})
    assert r.status_code == 201
    return r.json()