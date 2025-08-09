import pytest
from sqlalchemy.orm import Session
from app.models.book import Book
from app.models.member import Member
from app.models.borrow import Borrow
from app.tasks.email_tasks import check_overdue_books
from datetime import datetime, timedelta
from unittest.mock import patch


@pytest.mark.asyncio
async def test_overdue_notification(db_session: Session, mock_smtp):
    """Test the overdue notification Celery task."""
    # Create an overdue borrow
    book = Book(title="1984", author="George Orwell",
                total_copies=5, available_copies=4)
    member = Member(email="test@example.com", name="Test User",
                    hashed_password="hashed")
    borrow = Borrow(
        book=book,
        member=member,
        created_at=datetime.utcnow() - timedelta(days=15),  # Overdue by 1 day
        notification_sent=False
    )
    db_session.add_all([book, member, borrow])
    db_session.commit()

    # Run the overdue notification task
    with patch("app.tasks.email_tasks.send_email") as mock_email:
        check_overdue_books()
        mock_email.assert_called_once()
        call_args = mock_email.call_args[0]
        assert call_args[0] == "test@example.com"
        assert "Overdue Book Reminder" in call_args[1]
        assert "1984" in call_args[2]

    # Verify notification_sent was updated
    db_session.refresh(borrow)
    assert borrow.notification_sent is True
