import pytest

def test_get_note_logs_success(client, db_session, test_user, test_note):
    login = client.post("/auth/login", json={"username": "testuser", "password": "testpass"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    # View note to create log
    client.get(f"/notes/{test_note.id}", headers=headers)
    response = client.get(f"/notes/{test_note.id}/logs", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert response.json()[0]["action"] == "view"

def test_get_note_logs_unauthorized(client, db_session, test_user, test_note):
    # Register another user
    client.post("/auth/register", json={"username": "other", "password": "pass"})
    login = client.post("/auth/login", json={"username": "other", "password": "pass"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/notes/{test_note.id}/logs", headers=headers)
    assert response.status_code == 404

def test_activity_log_on_edit(client, db_session, test_user, test_note):
    login = client.post("/auth/login", json={"username": "testuser", "password": "testpass"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    # Edit note
    client.put(f"/notes/{test_note.id}", json={"title": "Edited", "content": "Edited content"}, headers=headers)
    response = client.get(f"/notes/{test_note.id}/logs", headers=headers)
    assert response.status_code == 200
    assert any(log["action"] == "edit" for log in response.json())

def test_activity_log_on_restore(client, db_session, test_user, test_note):
    login = client.post("/auth/login", json={"username": "testuser", "password": "testpass"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    # Edit to create version
    client.put(f"/notes/{test_note.id}", json={"title": "Edited", "content": "Edited content"}, headers=headers)
    # Restore to version 1
    client.post(f"/versions/{test_note.id}/restore/1", headers=headers)
    response = client.get(f"/notes/{test_note.id}/logs", headers=headers)
    assert response.status_code == 200
    assert any(log["action"] == "restore" for log in response.json())

def test_get_logs_non_existent_note(client, db_session, test_user):
    login = client.post("/auth/login", json={"username": "testuser", "password": "testpass"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/notes/999/logs", headers=headers)  # Non-existent note ID
    assert response.status_code == 404

def test_logs_order_by_timestamp_desc(client, db_session, test_user, test_note):
    login = client.post("/auth/login", json={"username": "testuser", "password": "testpass"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    # Create multiple logs
    client.get(f"/notes/{test_note.id}", headers=headers)
    client.put(f"/notes/{test_note.id}", json={"title": "Edited", "content": "Edited content"}, headers=headers)
    response = client.get(f"/notes/{test_note.id}/logs", headers=headers)
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) >= 2
    # Check descending order (most recent first)
    for i in range(len(logs) - 1):
        assert logs[i]["timestamp"] >= logs[i + 1]["timestamp"]