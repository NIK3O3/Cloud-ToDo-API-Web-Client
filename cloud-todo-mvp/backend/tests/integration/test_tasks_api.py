API_HEADERS = {"X-API-Key": "test-api-key"}


def test_create_task_returns_201(client):
    response = client.post("/api/tasks", json={"title": "Prepare MVP"}, headers=API_HEADERS)

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Prepare MVP"
    assert body["status"] == "NEW"
    assert "createdAt" in body


def test_list_tasks_supports_filters_and_pagination(client):
    client.post("/api/tasks", json={"title": "First task", "priority": "LOW"}, headers=API_HEADERS)
    client.post("/api/tasks", json={"title": "Second task", "priority": "HIGH"}, headers=API_HEADERS)

    response = client.get("/api/tasks?priority=HIGH&limit=10&offset=0", headers=API_HEADERS)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["priority"] == "HIGH"


def test_patch_task_changes_status(client):
    create_response = client.post("/api/tasks", json={"title": "Move task"}, headers=API_HEADERS)
    task_id = create_response.json()["id"]

    response = client.patch(f"/api/tasks/{task_id}", json={"status": "DONE"}, headers=API_HEADERS)

    assert response.status_code == 200
    assert response.json()["status"] == "DONE"


def test_validation_error_uses_stable_format(client):
    response = client.post("/api/tasks", json={"title": "x"}, headers=API_HEADERS)

    assert response.status_code == 400
    body = response.json()
    assert body["code"] == "VALIDATION_ERROR"
    assert isinstance(body["details"], list)


def test_missing_api_key_returns_401(client):
    response = client.get("/api/tasks")

    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHORIZED"


def test_delete_task_returns_204_then_404(client):
    create_response = client.post("/api/tasks", json={"title": "Delete task"}, headers=API_HEADERS)
    task_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/tasks/{task_id}", headers=API_HEADERS)
    get_response = client.get(f"/api/tasks/{task_id}", headers=API_HEADERS)

    assert delete_response.status_code == 204
    assert get_response.status_code == 404
