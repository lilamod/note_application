import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.main import app
from fastapi.testclient import TestClient

@pytest.fixture(scope="session")
def engine():
    return create_engine("sqlite:///./test.db")

@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(engine, tables):
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_user(db_session):
    from app.models.user import User
    from app.auth.utils import hash_password
    user = User(username="testuser", hashed_password=hash_password("testpass"))
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_note(db_session, test_user):
    from app.models.note import Note
    note = Note(title="Test Note", content="Test content", owner_id=test_user.id)
    db_session.add(note)
    db_session.commit()
    db_session.refresh(note)
    return note