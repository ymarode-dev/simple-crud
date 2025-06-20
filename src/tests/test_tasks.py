import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database.database import Base
from auth.auth import get_db
from models import models

# --- Setup SQLite In-Memory Test DB ---
SQLALCHEMY_TEST_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool  # Keeps in-memory DB alive for session
)

TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# --- Dependency override ---
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# --- Automatically create tables before tests ---
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


# --- Test Fixtures ---
@pytest.fixture(scope="module")
def test_user():
    return {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "securepass"
    }

@pytest.fixture(scope="module")
def create_user(test_user):
    db = TestingSessionLocal()
    user = models.User(**test_user)
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


@pytest.fixture
def task_payload(create_user):
    return {
        "title": "Test Task",
        "context": "Testing context",
        "user_id": create_user.user_id,
        "status": False
    }

# --- Test Cases ---

def test_create_task(task_payload):
    response = client.post("/tasks", json=task_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["msg"] == "Task created successfully!"
    assert "task_id" in data

def test_create_duplicate_task(task_payload):
    response = client.post("/tasks", json=task_payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Task with the same title already exists for this user"

def test_get_task_by_id(task_payload):
    create_resp = client.post("/tasks", json={
        **task_payload,
        "title": "Unique Task"
    })
    task_id = create_resp.json()["task_id"]

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Unique Task"
    assert data["context"] == "Testing context"

def test_get_all_tasks(create_user):
    response = client.get(f"/tasks/user/{create_user.user_id}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_task(create_user):
    # Create a task
    resp = client.post("/tasks", json={
        "title": "Update Me",
        "context": "Old context",
        "user_id": create_user.user_id,
        "status": False
    })
    task_id = resp.json()["task_id"]

    # Update it
    response = client.put(f"/tasks/{task_id}", json={
        "title": "Updated Task",
        "context": "Updated context",
        "user_id": create_user.user_id,
        "status": True
    })

    assert response.status_code == 200
    assert response.json()["msg"] == "Task updated successfully"

    # Confirm update
    confirm = client.get(f"/tasks/{task_id}")
    data = confirm.json()
    assert data["title"] == "Updated Task"
    assert data["status"] is True

def test_delete_task(create_user):
    # Create a task to delete
    resp = client.post("/tasks", json={
        "title": "Delete Me",
        "context": "Delete context",
        "user_id": create_user.user_id,
        "status": False
    })
    task_id = resp.json()["task_id"]

    # Delete
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["msg"] == "Task deleted successfully"

    # Ensure it's gone
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 404
