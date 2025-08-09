import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models.base import get_db
from app.models.member import Member


@pytest.fixture
def client(db_session):
    """Create a FastAPI test client with overridden DB dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.rollback()  # Ensure session is clean
            db_session.close()
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def set_test_db():
    """Set TEST_DATABASE_URL for in-memory SQLite."""
    os.environ["TEST_DATABASE_URL"] = "sqlite:///:memory:"
    yield
    os.environ.pop("TEST_DATABASE_URL", None)


@pytest.mark.asyncio
async def test_login(client: TestClient, db_session: Session, set_test_db):
    """Test login endpoint with valid credentials."""
    # Create a member
    member = Member(email="test@example.com", name="Test User")
    member.set_password("testpassword")
    db_session.add(member)
    db_session.commit()

    # Test login
    response = await client.post("/api/v1/login", json={"email": "test@example.com", "password": "testpassword"})
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: TestClient, db_session: Session, set_test_db):
    """Test login endpoint with invalid credentials."""
    # Use unique email to avoid IntegrityError
    member = Member(email="unique@example.com", name="Test User")
    member.set_password("testpassword")
    db_session.add(member)
    db_session.commit()
    response = await client.post("/api/v1/login", json={"email": "unique@example.com", "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
