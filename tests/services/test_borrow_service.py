from datetime import datetime
import os
from unittest.mock import patch
import pytest
from sqlalchemy.orm import Session
from app.schemas.borrow import BorrowCreate
from app.services.borrow_service import borrow_book, return_book, \
    get_member_borrows
from app.models.book import Book
from app.models.member import Member
from app.models.borrow import Borrow
from fastapi import HTTPException


@pytest.fixture
def set_test_db():
    """Set TEST_DATABASE_URL for in-memory SQLite."""
    os.environ["TEST_DATABASE_URL"] = "sqlite:///:memory:"
    yield
    os.environ.pop("TEST_DATABASE_URL", None)


@pytest.mark.asyncio
async def test_borrow_book_v1(db_session: Session, set_test_db):
    """Test borrowing a book (v1)."""
    member = Member(email="unique_borrow1@example.com", name="Test User")
    member.set_password("testpassword")
    book = Book(title="1984", author="George Orwell", total_copies=5, available_copies=5)
    db_session.add_all([member, book])
    db_session.commit()
    borrow_data = BorrowCreate(book_id=book.id, member_id=member.id)
    with patch("app.tasks.email_tasks.send_borrow_email") as mock_email:
        borrow = await borrow_book(borrow_data, db_session)
        assert borrow.book_id == book.id
        assert db_session.query(Book).get(book.id).available_copies == 4
        mock_email.delay.assert_called_once_with(borrow.id)
    db_session.rollback()


@pytest.mark.asyncio
async def test_borrow_book_v2(db_session: Session, set_test_db):
    """Test borrowing a book (v2)."""
    member = Member(email="unique_borrow2@example.com", name="Test User")
    member.set_password("testpassword")
    book = Book(title="1984", author="George Orwell", total_copies=5, available_copies=5)
    db_session.add_all([member, book])
    db_session.commit()
    borrow_data = BorrowCreate(book_id=book.id, member_id=member.id)
    with patch("app.tasks.email_tasks.send_borrow_email") as mock_email:
        borrow = await borrow_book(borrow_data, db_session)  # Adjust for v2 if different
        assert borrow.book_id == book.id
        mock_email.delay.assert_called_once_with(borrow.id)
    db_session.rollback()


@pytest.mark.asyncio
async def test_borrow_book_no_copies(db_session: Session, set_test_db):
    """Test borrowing a book with no available copies."""
    member = Member(email="unique_borrow3@example.com", name="Test User")
    member.set_password("testpassword")
    book = Book(title="1984", author="George Orwell", total_copies=1, available_copies=0)
    db_session.add_all([member, book])
    db_session.commit()
    borrow_data = BorrowCreate(book_id=book.id, member_id=member.id)
    with pytest.raises(HTTPException) as exc:
        await borrow_book(borrow_data, db_session)
    assert exc.value.status_code == 400
    db_session.rollback()


@pytest.mark.asyncio
async def test_return_book_v1(db_session: Session, set_test_db):
    """Test returning a book (v1)."""
    member = Member(email="unique_borrow4@example.com", name="Test User")
    member.set_password("testpassword")
    book = Book(title="1984", author="George Orwell", total_copies=5, available_copies=4)
    borrow = Borrow(book_id=book.id, member_id=member.id, notification_sent=False)
    db_session.add_all([member, book, borrow])
    db_session.commit()
    with patch("app.tasks.email_tasks.send_return_email") as mock_email:
        returned_borrow = await return_book(borrow.id, db_session)
        assert returned_borrow.return_date is not None
        assert db_session.query(Book).get(book.id).available_copies == 5
        mock_email.delay.assert_called_once_with(borrow.id)
    db_session.rollback()


@pytest.mark.asyncio
async def test_return_book_already_returned(db_session: Session, set_test_db):
    """Test returning an already returned book."""
    member = Member(email="unique_borrow5@example.com", name="Test User")
    member.set_password("testpassword")
    book = Book(title="1984", author="George Orwell", total_copies=5, available_copies=5)
    borrow = Borrow(book_id=book.id, member_id=member.id, notification_sent=False, return_date=datetime.utcnow())
    db_session.add_all([member, book, borrow])
    db_session.commit()
    with pytest.raises(HTTPException) as exc:
        await return_book(borrow.id, db_session)
    assert exc.value.status_code == 400
    db_session.rollback()


@pytest.mark.asyncio
async def test_get_member_borrows(db_session: Session, set_test_db):
    """Test retrieving a member's borrows."""
    member = Member(email="unique_borrow6@example.com", name="Test User")
    member.set_password("testpassword")
    book = Book(title="1984", author="George Orwell", total_copies=5, available_copies=4)
    borrow = Borrow(book_id=book.id, member_id=member.id, notification_sent=False)
    db_session.add_all([member, book, borrow])
    db_session.commit()
    borrows = await get_member_borrows(member.id, db_session)
    assert len(borrows) == 1
    assert borrows[0].book_id == book.id
    db_session.rollback()
