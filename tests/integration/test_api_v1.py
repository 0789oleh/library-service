import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models.base import get_db
from app.models.book import Book
from app.models.member import Member
from app.services.auth_service import create_access_token
from unittest.mock import patch


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


@pytest.fixture
def auth_headers(db_session: Session):
    """Create valid JWT token headers."""
    member = Member(email="test@example.com", name="Test User")
    member.set_password("testpassword")
    db_session.add(member)
    db_session.commit()
    token = create_access_token({"sub": "test@example.com"})
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
def test_full_flow(client: TestClient, db_session: Session, auth_headers):
    """Test the full API flow: login, create book, borrow, return, list borrows."""
    # Create a member
    member = Member(email="test@example.com", name="Test User")
    member.set_password("testpassword")
    db_session.add(member)
    db_session.commit()

    # Login
    response = client.post("/api/v1/login", json={"email": "test@example.com", "password": "testpassword"})
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"

    # Create a book
    book_data = {"title": "1984", "author": "George Orwell", "total_copies": 5}
    response = client.post("/api/v1/books", json=book_data, headers=auth_headers)
    assert response.status_code == 200
    book_id = response.json()["id"]
    assert response.json()["available_copies"] == 5

    # Borrow the book
    with patch("app.tasks.email_tasks.send_borrow_email") as mock_email:
        response = client.post(
            "/api/v1/borrow",
            json={"book_id": book_id, "member_id": member.id},
            headers=auth_headers
        )
        assert response.status_code == 200
        borrow_id = response.json()["id"]
        assert response.json()["notification_sent"] is False
        assert db_session.query(Book).get(book_id).available_copies == 4
        mock_email.delay.assert_called_once_with(borrow_id)

    # List borrowed books
    response = client.get(f"/api/v1/borrow/member/{member.id}", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["book_id"] == book_id

    # Return the book
    response = client.post(f"/api/v1/borrow/{borrow_id}/return", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["return_date"] is not None
    assert response.json()["notification_sent"] is False
    assert db_session.query(Book).get(book_id).available_copies == 5

    # List borrowed books (should be empty)
    response = client.get(f"/api/v1/borrow/member/{member.id}", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 0
