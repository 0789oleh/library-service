import asyncio
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.borrow import Borrow
from app.models.member import Member
from app.models.book import Book
from datetime import datetime, timedelta
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
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        member = db.query(Member).filter(Member.id == member_id).first()
        book = db.query(Book).filter(Book.id == book_id).first()
        subject = "Book Borrowed"
        body = f"You have borrowed '{book.title}' by {book.author}."
        asyncio.run(send_email(member.email, subject, body))
    finally:
        db.close()


@app.task
def send_return_email(member_id: int, book_id: int):
    """Celery task to send return notification (v2 only)."""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        member = db.query(Member).filter(Member.id == member_id).first()
        book = db.query(Book).filter(Book.id == book_id).first()
        subject = "Book Returned"
        body = f"You have returned '{book.title}' by {book.author}."
        asyncio.run(send_email(member.email, subject, body))
    finally:
        db.close()


@app.task
def send_overdue_notification():
    """Celery task to send notifications for overdue books (v2 only)."""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        overdue_threshold = datetime.now() - timedelta(days=14)
        overdue_borrows = db.query(Borrow).filter(
            Borrow.return_date.is_(None),
            Borrow.created_at < overdue_threshold,
            Borrow.notification_sent.is_(False)
        ).all()

        for borrow in overdue_borrows:
            member = db.query(Member) \
                .filter(Member.id == borrow.member_id).first()
            book = db.query(Book).filter(Book.id == borrow.book_id).first()
            subject = "Overdue Book Reminder"
            body = f"""Your borrowed book {book.title} by {book.author}
            is overdue. Please return it soon."""

            asyncio.run(send_email(member.email, subject, body))
            borrow.notification_sent = True
        db.commit()
    finally:
        db.close()
