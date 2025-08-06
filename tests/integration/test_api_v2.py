import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.book import Book
from app.models.member import Member
from app.services.auth_service import get_password_hash
from unittest.mock import patch


@pytest.mark.asyncio
async def test_v2_full_flow(client: TestClient,
                            db_session: Session, mock_celery):
    """Test the full v2 API flow: login, create book, borrow, return,
    list borrows with notifications."""
    # Create a member
    hashed_password = get_password_hash("testpassword")
    member = Member(email="test@example.com", name="Test User",
                    hashed_password=hashed_password)
    db_session.add(member)
    db_session.commit()

    # Login
    response = client.post("/v2/auth/login",
                           json={"email": "test@example.com",
                                 "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Create a book
    book_data = {"title": "1984", "author": "George Orwell", "total_copies": 5}
    response = client.post("/v2/books/", json=book_data)
    assert response.status_code == 200
    book_id = response.json()["id"]
    assert response.json()["available_copies"] == 5

    # Borrow the book (with notification)
    with patch("app.tasks.email_tasks.send_borrow_email") as mock_email:
        response = client.post("/v2/borrow/", json={"book_id": book_id, "member_id": member.id})
        assert response.status_code == 200
        borrow_id = response.json()["id"]
        assert response.json()["notification_sent"] is True
        mock_email.delay.assert_called_once_with(member.id, book_id)
    assert db_session.query(Book).get(book_id).available_copies == 4

    # List borrowed books
    response = client.get(f"/v2/borrow/member/{member.id}")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["book_id"] == book_id

    # Return the book (with notification)
    with patch("app.tasks.email_tasks.send_return_email") as mock_email:
        response = client.post(f"/v2/borrow/{borrow_id}/return")
        assert response.status_code == 200
        assert response.json()["return_date"] is not None
        assert response.json()["notification_sent"] is True
        mock_email.delay.assert_called_once_with(member.id, book_id)
    assert db_session.query(Book).get(book_id).available_copies == 5

    # List borrowed books (should be empty)
    response = client.get(f"/v2/borrow/member/{member.id}")
    assert response.status_code == 200
    assert len(response.json()) == 0
