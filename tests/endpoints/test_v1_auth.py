import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models.member import Member
from app.services.auth_service import get_password_hash


@pytest.fixture
def client(db_session):
    """Create a FastAPI test client with overridden DB dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    app.dependency_overrides[app.get_db] = override_get_db
    return TestClient(app)


@pytest.mark.asyncio
async def test_v1_login(client: TestClient, db_session: Session):
    """Test v1 login endpoint."""
    hashed_password = get_password_hash("testpassword")
    member = Member(email="test@example.com", name="Test User",
                    hashed_password=hashed_password)
    db_session.add(member)
    db_session.commit()

    response = client.post("/v1/auth/login", json={"email": "test@example.com",
                                                   "password": "testpassword"})
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert "access_token" in response.json()
