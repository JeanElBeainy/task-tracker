import pytest

from app.models import TaskStatus


# ---------------------------------------------------------------------------
# POST /tasks
# ---------------------------------------------------------------------------

def test_create_task_valid_returns_201_with_full_body(client):
    payload = {
        "title": "Write tests",
        "description": "Cover the REST endpoints",
        "status": "ToDo",
        "priority": "High",
        "assignee": "jean",
    }
    r = client.post("/tasks", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["title"] == "Write tests"
    assert body["description"] == "Cover the REST endpoints"
    assert body["status"] == "ToDo"
    assert body["priority"] == "High"
    assert body["assignee"] == "jean"
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


def test_create_task_missing_title_returns_422(client):
    r = client.post("/tasks", json={"priority": "Low"})
    assert r.status_code == 422


def test_create_task_blank_title_returns_422(client):
    r = client.post("/tasks", json={"title": "   "})
    assert r.status_code == 422


def test_create_task_invalid_priority_returns_422(client):
    r = client.post("/tasks", json={"title": "ok", "priority": "Urgent"})
    assert r.status_code == 422


def test_create_task_unknown_field_returns_422(client):
    r = client.post("/tasks", json={"title": "ok", "color": "red"})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# GET /tasks
# ---------------------------------------------------------------------------

def test_list_tasks_empty_returns_200_and_empty_list(client):
    r = client.get("/tasks")
    assert r.status_code == 200
    assert r.json() == []


def test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list(client):
    # Create a ToDo task, then query for InProgress — should be empty.
    client.post("/tasks", json={"title": "t1", "status": "ToDo"})
    r = client.get("/tasks", params={"status": "InProgress"})
    assert r.status_code == 200
    assert r.json() == []


def test_list_tasks_filter_by_priority_returns_only_matches(client):
    client.post("/tasks", json={"title": "low-task", "priority": "Low"})
    client.post("/tasks", json={"title": "high-task", "priority": "High"})
    r = client.get("/tasks", params={"priority": "High"})
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["title"] == "high-task"


# ---------------------------------------------------------------------------
# GET /tasks/{id}
# ---------------------------------------------------------------------------

def test_get_task_by_id_returns_task(client, created_task):
    task_id = created_task["id"]
    r = client.get(f"/tasks/{task_id}")
    assert r.status_code == 200
    assert r.json()["id"] == task_id


def test_get_task_by_id_not_found_returns_404_with_detail(client):
    r = client.get("/tasks/nonexistent-id")
    assert r.status_code == 404
    assert "detail" in r.json()


# ---------------------------------------------------------------------------
# PATCH /tasks/{id}
# ---------------------------------------------------------------------------

def test_patch_partial_update_keeps_other_fields(client, created_task):
    task_id = created_task["id"]
    r = client.patch(f"/tasks/{task_id}", json={"title": "updated title"})
    assert r.status_code == 200
    body = r.json()
    assert body["title"] == "updated title"
    # Other fields remain unchanged.
    assert body["status"] == created_task["status"]
    assert body["priority"] == created_task["priority"]
    assert body["description"] == created_task["description"]


def test_patch_not_found_returns_404(client):
    r = client.patch("/tasks/nonexistent-id", json={"title": "nope"})
    assert r.status_code == 404


def test_patch_valid_transition_todo_to_inprogress_returns_200(client, created_task):
    task_id = created_task["id"]
    r = client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})
    assert r.status_code == 200
    assert r.json()["status"] == "InProgress"


def test_patch_invalid_transition_todo_to_done_returns_422(client, created_task):
    task_id = created_task["id"]
    r = client.patch(f"/tasks/{task_id}", json={"status": "Done"})
    assert r.status_code == 422


def test_patch_same_status_is_noop_returns_200(client, created_task):
    task_id = created_task["id"]
    # created_task defaults to "ToDo" — patching to the same status is a no-op.
    r = client.patch(f"/tasks/{task_id}", json={"status": "ToDo"})
    assert r.status_code == 200


def test_patch_invalid_status_value_not_in_enum_returns_422(client, created_task):
    task_id = created_task["id"]
    r = client.patch(f"/tasks/{task_id}", json={"status": "BogusStatus"})
    assert r.status_code == 422
    assert "detail" in r.json()


def test_patch_empty_body_returns_200_unchanged(client, created_task):
    task_id = created_task["id"]
    r = client.patch(f"/tasks/{task_id}", json={})
    assert r.status_code == 200
    body = r.json()
    assert body["title"] == created_task["title"]
    assert body["status"] == created_task["status"]


def test_patch_invalid_priority_value_not_in_enum_returns_422(client, created_task):
    task_id = created_task["id"]
    r = client.patch(f"/tasks/{task_id}", json={"priority": "Urgent"})
    assert r.status_code == 422
    assert "detail" in r.json()


def test_patch_unknown_field_returns_422(client, created_task):
    task_id = created_task["id"]
    r = client.patch(f"/tasks/{task_id}", json={"color": "red"})
    assert r.status_code == 422
    assert "detail" in r.json()


def test_patch_blank_title_returns_422(client, created_task):
    task_id = created_task["id"]
    r = client.patch(f"/tasks/{task_id}", json={"title": "   "})
    assert r.status_code == 422
    assert "detail" in r.json()


def test_patch_wrong_type_for_enum_field_returns_422(client, created_task):
    task_id = created_task["id"]
    r = client.patch(f"/tasks/{task_id}", json={"priority": 42})
    assert r.status_code == 422
    assert "detail" in r.json()


# ---------------------------------------------------------------------------
# DELETE /tasks/{id}
# ---------------------------------------------------------------------------

def test_delete_existing_returns_204_no_body(client, created_task):
    task_id = created_task["id"]
    r = client.delete(f"/tasks/{task_id}")
    assert r.status_code == 204
    assert r.content == b""


def test_delete_missing_returns_404(client):
    r = client.delete("/tasks/nonexistent-id")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# POST /tasks — due_date
# ---------------------------------------------------------------------------

def test_create_task_with_valid_due_date_returns_201_with_date(client):
    payload = {
        "title": "Due date task",
        "due_date": "2025-12-31",
    }
    r = client.post("/tasks", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["due_date"] == "2025-12-31"


def test_create_task_with_invalid_due_date_format_returns_422(client):
    payload = {
        "title": "Bad date",
        "due_date": "12/31/2025",
    }
    r = client.post("/tasks", json=payload)
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# GET /tasks — overdue filter
# ---------------------------------------------------------------------------

def test_list_tasks_overdue_includes_past_due_date_with_status_todo(client):
    client.post("/tasks", json={
        "title": "overdue task",
        "due_date": "2020-01-01",
        "status": "ToDo",
    })
    r = client.get("/tasks", params={"overdue": True})
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["title"] == "overdue task"
    assert data[0]["due_date"] == "2020-01-01"


def test_list_tasks_overdue_excludes_past_due_date_with_status_done(client):
    client.post("/tasks", json={
        "title": "finished late",
        "due_date": "2020-01-01",
        "status": "Done",
    })
    r = client.get("/tasks", params={"overdue": True})
    assert r.status_code == 200
    assert r.json() == []


def test_list_tasks_overdue_with_no_matches_returns_200_and_empty_list(client):
    r = client.get("/tasks", params={"overdue": True})
    assert r.status_code == 200
    assert r.json() == []