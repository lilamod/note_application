import pytest

def test_search_notes_success(client, db_session, test_user, test_note):
    login = client.post("/auth/login", json={"username": "testuser", "password": "testpass"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/notes/search?query=test", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1

def test_search_notes_no_results(client, db_session, test_user):
    login = client.post("/auth/login", json={"username": "testuser", "password": "testpass"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/notes/search?query=nonexistent", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 0

def test_search_notes_unauthorized(client):
    response = client.get("/notes/search?query=test")
    assert response.status_code == 401