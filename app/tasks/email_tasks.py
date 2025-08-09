import logging
from celery import Celery
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.core.config import get_settings
from app.models.borrow import Borrow
from app.models.member import Member
from app.models.book import Book
from datetime import datetime, timedelta
import aiosmtplib
from email.message import EmailMessage
import urllib.parse

logger = logging.getLogger(__name__)


def get_celery_app():
    settings = get_settings()
    logger.info(f"REDIS_URL: {settings.REDIS_URL}")
    return Celery("tasks", broker=settings.REDIS_URL,
                  include=['app.tasks.email_tasks'])


app = get_celery_app()


async def send_email(to_email: str, subject: str, body: str):
    settings = get_settings()
    message = EmailMessage()
    message.set_content(body)
    message["Subject"] = subject
    message["From"] = settings.SMTP_USER
    message["To"] = to_email
    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=True,
        )
        logger.info(f"Email sent to {to_email}")
        return {"status": "Email sent"}
    except Exception as e:
        logger.error(f"Email sending error: {e}")
        return {"error": str(e)}


@app.task(name="app.tasks.email_tasks.send_borrow_email",
          bind=True, max_retries=3)
def send_borrow_email(self, borrow_id: int):
    settings = get_settings()
    try:
        logger.info(f"""Attempting to connect to DATABASE_URL:
                    {settings.DATABASE_URL}""")
        parsed_url = urllib.parse.urlparse(settings.DATABASE_URL)
        logger.info(f"""Parsed DATABASE_URL: scheme={parsed_url.scheme},
                    host={parsed_url.hostname}, port={parsed_url.port},
                    path={parsed_url.path}""")
        if parsed_url.path != '/library_db':
            raise ValueError(f"""Invalid database name in DATABASE_URL:
                             {parsed_url.path}, expected '/library_db'""")
        engine = create_engine(settings.DATABASE_URL, echo=True,
                               connect_args={'dbname': 'library_db'})
        conn = engine.connect()
        logger.info(f"Successfully connected to database: {conn}")
        conn.close()
        SessionLocal = sessionmaker(autocommit=False,
                                    autoflush=False, bind=engine)
        session = SessionLocal()
        try:
            borrow = session.query(Borrow).get(borrow_id)
            if not borrow:
                logger.error(f"Borrow record {borrow_id} not found")
                return {"error": f"Borrow record {borrow_id} not found"}
            member = session.query(Member).get(borrow.member_id)
            book = session.query(Book).get(borrow.book_id)
            if not member or not book:
                logger.error("Member or book not found")
                return {"error": "Member or book not found"}
            subject = f"Book Borrowed: {book.title}"
            body = f"""Dear {member.name},\n\nYou have borrowed '{book.title}'
            on {borrow.borrow_date}.Please return it by
            {borrow.borrow_date + timedelta(days=14)}.\n\nThank you."""
            send_email.delay(member.email, subject, body)
            logger.info(f"""Borrow email task triggered
                        for borrow_id: {borrow_id}""")
            return {"status": "Borrow email sent"}
        except Exception as e:
            logger.error(f"send_borrow_email error: {e}")
            return {"error": str(e)}
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Database connection error in send_borrow_email: {e}")
        self.retry(countdown=60, exc=e)


@app.task(name="app.tasks.email_tasks.send_return_email",
          bind=True, max_retries=3)
def send_return_email(self, borrow_id: int):
    settings = get_settings()
    try:
        logger.info(f"""Attempting to connect to
                    DATABASE_URL: {settings.DATABASE_URL}""")
        parsed_url = urllib.parse.urlparse(settings.DATABASE_URL)
        logger.info(f"Parsed DATABASE_URL: scheme={parsed_url.scheme}, host={parsed_url.hostname}, port={parsed_url.port}, path={parsed_url.path}")
        if parsed_url.path != '/library_db':
            raise ValueError(f"Invalid database name in DATABASE_URL: {parsed_url.path}, expected '/library_db'")
        engine = create_engine(settings.DATABASE_URL, echo=True, connect_args={'dbname': 'library_db'})
        conn = engine.connect()
        logger.info(f"Successfully connected to database: {conn}")
        conn.close()
        SessionLocal = sessionmaker(autocommit=False,
                                    autoflush=False, bind=engine)
        session = SessionLocal()
        try:
            borrow = session.query(Borrow).get(borrow_id)
            if not borrow:
                logger.error(f"Borrow record {borrow_id} not found")
                return {"error": f"Borrow record {borrow_id} not found"}
            member = session.query(Member).get(borrow.member_id)
            book = session.query(Book).get(borrow.book_id)
            if not member or not book:
                logger.error("Member or book not found")
                return {"error": "Member or book not found"}
            subject = f"Book Returned: {book.title}"
            body = f"Dear {member.name},\n\nYou have returned '{book.title}' on {borrow.return_date}. Thank you for using our library.\n\nBest regards."
            send_email.delay(member.email, subject, body)
            logger.info(f"Return email task triggered for borrow_id: {borrow_id}")
            return {"status": "Return email sent"}
        except Exception as e:
            logger.error(f"send_return_email error: {e}")
            return {"error": str(e)}
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Database connection error in send_return_email: {e}")
        self.retry(countdown=60, exc=e)


@app.task(name="app.tasks.email_tasks.check_overdue_books",
          bind=True, max_retries=3)
def check_overdue_books(self):
    settings = get_settings()
    try:
        logger.info(f"Attempting to connect to DATABASE_URL: {settings.DATABASE_URL}")
        parsed_url = urllib.parse.urlparse(settings.DATABASE_URL)
        logger.info(f"Parsed DATABASE_URL: scheme={parsed_url.scheme}, host={parsed_url.hostname}, port={parsed_url.port}, path={parsed_url.path}")
        if parsed_url.path != '/library_db':
            raise ValueError(f"Invalid database name in DATABASE_URL: {parsed_url.path}, expected '/library_db'")
        engine = create_engine(settings.DATABASE_URL, echo=True, connect_args={'dbname': 'library_db'})
        conn = engine.connect()
        logger.info(f"Successfully connected to database: {conn}")
        conn.close()
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        try:
            overdue_date = datetime.now() - timedelta(days=14)
            overdue_borrows = session.query(Borrow).filter(Borrow.return_date is None, Borrow.borrow_date < overdue_date).all()
            for borrow in overdue_borrows:
                member = session.query(Member).get(borrow.member_id)
                book = session.query(Book).get(borrow.book_id)
                if member and book:
                    subject = f"Overdue Book: {book.title}"
                    body = f"""Dear {member.name},\n\nThe book '{book.title}'
                    is overdue. Please return it.\n\nThank you."""
                    send_email.delay(member.email, subject, body)
                    logger.info(f"Overdue email task triggered for borrow_id: {borrow.id}")
            return {"status": "Overdue emails sent"}
        except Exception as e:
            logger.error(f"check_overdue_books error: {e}")
            return {"error": str(e)}
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Database connection error in check_overdue_books: {e}")
        self.retry(countdown=60, exc=e)
