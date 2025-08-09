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
            db_session.close()
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.mark.asyncio
async def test_login(client: TestClient, db_session: Session):
    """Test login endpoint with valid credentials."""
    member = Member(email="test@example.com", name="Test User")
    member.set_password("testpassword")
    db_session.add(member)
    db_session.commit()

    response = client.post("/api/v2/login", json={"email": "test@example.com", "password": "testpassword"})
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert "access_token" in response.json()


async def test_login_invalid_credentials(client: TestClient, db_session: Session):
    """Test login endpoint with invalid credentials."""
    member = Member(email="test@example.com", name="Test User")
    member.set_password("testpassword")
    db_session.add(member)
    db_session.commit()

    # Wrong password
    response = client.post("/api/v2/login", json={"email": "test@example.com", "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

    # Non-existent email
    response = client.post("/api/v2/login", json={"email": "nonexistent@example.com", "password": "testpassword"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
