from celery import Celery
from app.core.config import settings
import aiosmtplib
from email.message import EmailMessage

app = Celery("tasks", broker=settings.REDIS_URL)


async def send_email(to_email: str, subject: str, body: str):
    """Send an email asynchronously."""
    message = EmailMessage()
    message.set_content(body)
    message["Subject"] = subject
    message["From"] = settings.SMTP_USER
    message["To"] = to_email

    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        use_tls=True,
    )


@app.task
def send_borrow_email(member_id: int, book_id: int):
    """Celery task to send borrow notification (v2 only)."""
    # In a real app, fetch member and book details from DB
    subject = "Book Borrowed"
    body = f"You have borrowed book ID {book_id}."
    to_email = "user@example.com"  # Placeholder; fetch from DB
    import asyncio
    asyncio.run(send_email(to_email, subject, body))


@app.task
def send_return_email(member_id: int, book_id: int):
    """Celery task to send return notification (v2 only)."""
    subject = "Book Returned"
    body = f"You have returned book ID {book_id}."
    to_email = "user@example.com"  # Placeholder; fetch from DB
    import asyncio
    asyncio.run(send_email(to_email, subject, body))
