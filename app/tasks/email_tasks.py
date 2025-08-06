from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings
from app.models.borrow import Borrow
from app.models.member import Member
from app.models.book import Book
from datetime import datetime, timedelta
import aiosmtplib
from email.message import EmailMessage


def get_celery_app():
    settings = get_settings()
    return Celery("tasks", broker=settings.REDIS_URL)


app = get_celery_app()


async def send_email(to_email: str, subject: str, body: str):
    settings = get_settings()
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
def check_overdue_books():
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        overdue_date = datetime.utcnow() - timedelta(days=14)
        overdue_borrows = session.query(Borrow)\
            .filter(Borrow.return_date is None,
                    Borrow.borrow_date < overdue_date).all()
        for borrow in overdue_borrows:
            member = session.query(Member).get(borrow.member_id)
            book = session.query(Book).get(borrow.book_id)
            subject = f"Overdue Book: {book.title}"
            body = f"""Dear {member.name},\n\nThe book '{book.title}'
            is overdue. Please return it.\n\nThank you."""
            send_email.delay(member.email, subject, body)
    finally:
        session.close()


@app.task
def send_borrow_email(borrow_id: int):
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        borrow = session.query(Borrow).get(borrow_id)
        if not borrow:
            return {"error": f"Borrow record {borrow_id} not found"}
        member = session.query(Member).get(borrow.member_id)
        book = session.query(Book).get(borrow.book_id)
        subject = f"Book Borrowed: {book.title}"
        body = f"""Dear {member.name},\n\nYou have borrowed '{book.title}' on
        {borrow.borrow_date}. Please return it by
        {borrow.borrow_date + timedelta(days=14)}.\n\nThank you."""
        send_email.delay(member.email, subject, body)
        return {"status": "Borrow email sent"}
    finally:
        session.close()


@app.task
def send_return_email(borrow_id: int):
    settings = get_settings()
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        borrow = session.query(Borrow).get(borrow_id)
        if not borrow:
            return {"error": f"Borrow record {borrow_id} not found"}
        member = session.query(Member).get(borrow.member_id)
        book = session.query(Book).get(borrow.book_id)
        subject = f"Book Returned: {book.title}"
        body = f"""Dear {member.name},\n\nYou have returned '{book.title}' on
          {borrow.return_date}. Thank you for using our library.\n\n
          Best regards."""
        send_email.delay(member.email, subject, body)
        return {"status": "Return email sent"}
    finally:
        session.close()
