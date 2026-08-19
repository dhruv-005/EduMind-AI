import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from main import app

# Test database
TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture(scope="function")
def db():
    """Create test database."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create test client."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    """Get auth headers for test user."""
    # Register test user
    client.post("/api/v1/auth/register", json={
        "email": "test@test.com",
        "password": "test1234",
        "full_name": "Test User",
        "role": "student"
    })
    # Login
    response = client.post("/api/v1/auth/login", json={
        "email": "test@test.com",
        "password": "test1234"
    })
    token = response.json()["data"]["token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client):
    """Get admin auth headers."""
    client.post("/api/v1/auth/register", json={
        "email": "admin@test.com",
        "password": "admin1234",
        "full_name": "Admin User",
        "role": "admin"
    })
    response = client.post("/api/v1/auth/login", json={
        "email": "admin@test.com",
        "password": "admin1234"
    })
    token = response.json()["data"]["token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_evaluation_request():
    """Sample evaluation request data."""
    return {
        "question": "What is photosynthesis?",
        "reference_answer": (
            "Photosynthesis is the process by which plants "
            "use sunlight, water, and carbon dioxide to produce "
            "oxygen and energy in the form of sugar."
        ),
        "student_answer": (
            "Photosynthesis is when plants make food "
            "using sunlight and water."
        ),
        "subject": "science",
        "grade_level": "Grade 8",
        "max_score": 10.0
    }
