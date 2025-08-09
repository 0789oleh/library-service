import pytest
from fastapi.testclient import TestClient
from app.main import app


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


async def test_v1_create_book(client: TestClient):
    """Test v1 book creation endpoint."""
    book_data = {"title": "1984", "author": "George Orwell", "total_copies": 5}
    response = client.post("/v1/books/", json=book_data)
    assert response.status_code == 200
    assert response.json()["title"] == "1984"
    assert response.json()["available_copies"] == 5
