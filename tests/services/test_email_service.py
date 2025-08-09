import pytest
from unittest.mock import patch
from app.tasks.email_tasks import send_email, send_borrow_email, send_return_email
from app.models.borrow import Borrow


@pytest.mark.asyncio
async def test_send_email():
    """Test sending a generic email."""
    with patch("aiosmtplib.send") as mock_send:
        result = await send_email("test@example.com", "Test Subject", "Test Body")
        assert result == {"status": "Email sent"}
        mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_send_borrow_email(db_session):
    """Test sending a borrow notification email."""
    borrow = Borrow(id=1, book_id=1, member_id=1, notification_sent=False)
    db_session.add(borrow)
    db_session.commit()
    with patch("aiosmtplib.send") as mock_send:
        result = await send_borrow_email(borrow.id, db_session)
        assert result == {"status": "Email sent"}
        mock_send.assert_called_once()
    db_session.rollback()


@pytest.mark.asyncio
async def test_send_return_email(db_session):
    """Test sending a return notification email."""
    borrow = Borrow(id=1, book_id=1, member_id=1, notification_sent=False)
    db_session.add(borrow)
    db_session.commit()
    with patch("aiosmtplib.send") as mock_send:
        result = await send_return_email(borrow.id, db_session)
        assert result == {"status": "Email sent"}
        mock_send.assert_called_once()
    db_session.rollback()
