import pytest
from sqlalchemy.orm import Session
from app.models.book import Book
from app.models.member import Member
from app.models.borrow import Borrow
from unittest.mock import patch
from app.tasks.email_tasks import send_overdue_notification
from datetime import datetime, timedelta
import os


@pytest.fixture
def set_test_db():
    """Set TEST_DATABASE_URL for in-memory SQLite."""
    os.environ["TEST_DATABASE_URL"] = "sqlite:///:memory:"
    yield
    os.environ.pop("TEST_DATABASE_URL", None)


@pytest.mark.asyncio
async def test_overdue_notification(db_session: Session, set_test_db):
    """Test sending overdue notification."""
    unique_email = f"overdue_{int(datetime.utcnow().timestamp())}@example.com"
    member = Member(email=unique_email, name="Test User")
    member.set_password("testpassword")
    book = Book(title="1984", author="George Orwell", total_copies=5, available_copies=4)
    borrow = Borrow(
        book_id=book.id,
        member_id=member.id,
        notification_sent=False,
        created_at=datetime.utcnow() - timedelta(days=15)  # Overdue
    )
    db_session.add_all([member, book, borrow])
    db_session.commit()
    with patch("app.tasks.email_tasks.send_email") as mock_email:
        await send_overdue_notification(borrow.id, db_session)
        assert db_session.query(Borrow).get(borrow.id).notification_sent is True
        mock_email.assert_called_once()
    db_session.rollback()
