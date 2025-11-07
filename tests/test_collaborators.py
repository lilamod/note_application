import pytest
from app.models.user import User
from app.models.note import Note

def test_add_collaborator_success(client, db_session, test_user, test_note):
    client.post("/auth/register", json={"username": "collab", "password": "pass"})
    login = client.post("/auth/login", json={"username": "testuser", "password": "testpass"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(f"/notes/{test_note.id}/collaborators", json={"username": "collab"}, headers=headers)
    assert response.status_code == 200
    assert "added" in response.json()["message"]

def test_add_collaborator_not_owner(client, db_session, test_user, test_note):
    client.post("/auth/register", json={"username": "other", "password": "pass"})
    login = client.post("/auth/login", json={"username": "other", "password": "pass"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(f"/notes/{test_note.id}/collaborators", json={"username": "collab"}, headers=headers)
    assert response.status_code == 404

def test_remove_collaborator_success(client, db_session, test_user, test_note):
    client.post("/auth/register", json={"username": "collab", "password": "pass"})
    login = client.post("/auth/login", json={"username": "testuser", "password": "testpass"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.post(f"/notes/{test_note.id}/collaborators", json={"username": "collab"}, headers=headers)
    collab_user = db_session.query(User).filter(User.username == "collab").first()
    response = client.delete(f"/notes/{test_note.id}/collaborators/{collab_user.id}", headers=headers)
    assert response.status_code == 200
    assert "removed" in response.json()["message"]

def test_collaborator_edit_note(client, db_session, test_user, test_note):
    # Add collaborator
    client.post("/auth/register", json={"username": "collab", "password": "pass"})
    login = client.post("/auth/login", json={"username": "testuser", "password": "testpass"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.post(f"/notes/{test_note.id}/collaborators", json={"username": "collab"}, headers=headers)
    login_collab = client.post("/auth/login", json={"username": "collab", "password": "pass"})
    token_collab = login_collab.json()["access_token"]
    headers_collab = {"Authorization": f"Bearer {token_collab}"}
    response = client.put(f"/notes/{test_note.id}", json={"title": "Updated", "content": "Updated content"}, headers=headers_collab)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"