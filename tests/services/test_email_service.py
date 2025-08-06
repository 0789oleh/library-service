import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from app.services.email_service import send_email, send_borrow_email, \
    send_return_email


@pytest.mark.asyncio
async def test_send_email(mock_smtp):
    """Test sending an email."""
    await send_email("test@example.com", "Test Subject", "Test Body")
    mock_smtp.assert_called_once()
    call_args = mock_smtp.call_args[0][0]
    assert call_args["To"] == "test@example.com"
    assert call_args["Subject"] == "Test Subject"
    assert "Test Body" in str(call_args.get_content())


def test_send_borrow_email(mock_celery):
    """Test Celery task for borrow email."""
    send_borrow_email(1, 1)
    mock_celery.assert_called_once()
    assert mock_celery.call_args[0][0] == send_borrow_email


def test_send_return_email(mock_celery):
    """Test Celery task for return email."""
    send_return_email(1, 1)
    mock_celery.assert_called_once()
    assert mock_celery.call_args[0][0] == send_return_email
