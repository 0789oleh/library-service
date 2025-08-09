import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
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
    app.dependency_overrides[app.get_db] = override_get_db
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


async def test_borrow_book_authorized(client: TestClient, db_session: Session, auth_headers):
    """Test borrow book endpoint with valid authorization."""
    book = Book(title="1984", author="George Orwell", total_copies=5, available_copies=5)
    member = db_session.query(Member).filter(Member.email == "test@example.com").first()
    db_session.add(book)
    db_session.commit()

    with patch("app.tasks.email_tasks.send_borrow_email") as mock_email:
        response = client.post(
            "/api/v1/borrow",
            json={"book_id": book.id, "member_id": member.id},
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["book_id"] == book.id
        assert response.json()["notification_sent"] is False  # Align with Borrow model
        mock_email.delay.assert_called_once_with(response.json()["id"])


async def test_borrow_book_unauthorized(client: TestClient, db_session: Session):
    """Test borrow book endpoint with missing/invalid token."""
    book = Book(title="1984", author="George Orwell", total_copies=5, available_copies=5)
    member = Member(email="test@example.com", name="Test User")
    member.set_password("testpassword")
    db_session.add_all([book, member])
    db_session.commit()

    response = client.post("/api/v1/borrow", json={"book_id": book.id, "member_id": member.id})
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

    response = client.post(
        "/api/v1/borrow",
        json={"book_id": book.id, "member_id": member.id},
        headers={"Authorization": "Bearer invalid"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"
