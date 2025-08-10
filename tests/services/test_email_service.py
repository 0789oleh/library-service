import pytest
from unittest.mock import patch
from app.tasks.email_tasks import send_email, send_borrow_email, send_return_email
from app.models.borrow import Borrow
from app.models.member import Member
from app.models.book import Book
from sqlalchemy.orm import Session
from datetime import datetime
import os


@pytest.fixture
def set_test_db():
    """Set TEST_DATABASE_URL for in-memory SQLite."""
    os.environ["TEST_DATABASE_URL"] = "sqlite:///:memory:"
    yield
    os.environ.pop("TEST_DATABASE_URL", None)


@pytest.mark.asyncio
async def test_send_email():
    """Test sending a generic email."""
    with patch("aiosmtplib.send") as mock_send:
        result = await send_email("test@example.com", "Test Subject", "Test Body")
        assert result == {"status": "Email sent"}
        mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_send_borrow_email(db_session: Session, set_test_db):
    """Test sending a borrow notification email."""
    unique_email = f"borrow_email_{int(datetime.utcnow().timestamp())}@example.com"
    member = Member(email=unique_email, name="Test User")
    member.set_password("testpassword")
    book = Book(title="1984", author="George Orwell", total_copies=5, available_copies=5)
    db_session.add_all([member, book])
    db_session.commit()  # Commit to assign IDs
    borrow = Borrow(book_id=book.id, member_id=member.id, notification_sent=False)
    db_session.add(borrow)
    db_session.commit()
    with patch("aiosmtplib.send") as mock_send:
        result = await send_borrow_email(borrow.id, db_session)
        assert result == {"status": "Email sent"}
        assert db_session.query(Borrow).get(borrow.id).notification_sent is True
        mock_send.assert_called_once()
    db_session.rollback()


@pytest.mark.asyncio
async def test_send_return_email(db_session: Session, set_test_db):
    """Test sending a return notification email."""
    unique_email = f"return_email_{int(datetime.utcnow().timestamp())}@example.com"
    member = Member(email=unique_email, name="Test User")
    member.set_password("testpassword")
    book = Book(title="1984", author="George Orwell", total_copies=5, available_copies=5)
    db_session.add_all([member, book])
    db_session.commit()  # Commit to assign IDs
    borrow = Borrow(book_id=book.id, member_id=member.id, notification_sent=False)
    db_session.add(borrow)
    db_session.commit()
    with patch("aiosmtplib.send") as mock_send:
        result = await send_return_email(borrow.id, db_session)
        assert result == {"status": "Email sent"}
        assert db_session.query(Borrow).get(borrow.id).notification_sent is True
        mock_send.assert_called_once()
    db_session.rollback()
