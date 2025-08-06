from datetime import datetime, timezone
import pytest
from sqlalchemy.orm import Session
from app.services.borrow_service import borrow_book, return_book, \
    get_member_borrows
from app.models.book import Book
from app.models.member import Member
from app.models.borrow import Borrow
from fastapi import HTTPException


def test_borrow_book_v1(db_session: Session):
    """Test borrowing a book in v1 (no notification)."""
    book = Book(title="1984", author="George Orwell",
                total_copies=5, available_copies=5)
    member = Member(email="test@example.com", name="Test User",
                    hashed_password="hashed")
    db_session.add_all([book, member])
    db_session.commit()

    borrow = borrow_book(db_session, book.id, member.id, api_version="v1")
    assert borrow.book_id == book.id
    assert borrow.member_id == member.id
    assert borrow.notification_sent is False
    assert db_session.query(Book).get(book.id).available_copies == 4


def test_borrow_book_v2(db_session: Session):
    """Test borrowing a book in v2 (with notification)."""
    book = Book(title="1984", author="George Orwell",
                total_copies=5, available_copies=5)
    member = Member(email="test@example.com", name="Test User",
                    hashed_password="hashed")
    db_session.add_all([book, member])
    db_session.commit()

    borrow = borrow_book(db_session, book.id, member.id, api_version="v2")
    assert borrow.notification_sent is True
    assert db_session.query(Book).get(book.id).available_copies == 4


def test_borrow_book_no_copies(db_session: Session):
    """Test borrowing when no copies are available."""
    book = Book(title="1984", author="George Orwell", total_copies=1,
                available_copies=0)
    member = Member(email="test@example.com", name="Test User",
                    hashed_password="hashed")
    db_session.add_all([book, member])
    db_session.commit()

    with pytest.raises(HTTPException) as exc:
        borrow_book(db_session, book.id, member.id)
    assert exc.value.status_code == 400
    assert exc.value.detail == "No copies available"


def test_return_book_v1(db_session: Session):
    """Test returning a book in v1 (no notification)."""
    book = Book(title="1984", author="George Orwell",
                total_copies=5, available_copies=4)
    member = Member(email="test@example.com", name="Test User",
                    hashed_password="hashed")
    borrow = Borrow(book=book, member=member, notification_sent=False)
    db_session.add_all([book, member, borrow])
    db_session.commit()

    returned_borrow = return_book(db_session, borrow.id, api_version="v1")
    assert returned_borrow.return_date is not None
    assert returned_borrow.notification_sent is False
    assert db_session.query(Book).get(book.id).available_copies == 5


def test_return_book_already_returned(db_session: Session):
    """Test returning an already returned book."""
    book = Book(title="1984", author="George Orwell",
                total_copies=5, available_copies=4)
    member = Member(email="test@example.com", name="Test User",
                    hashed_password="hashed")
    borrow = Borrow(book=book, member=member,
                    return_date=datetime.now(timezone.utc),)
    db_session.add_all([book, member, borrow])
    db_session.commit()

    with pytest.raises(HTTPException) as exc:
        return_book(db_session, borrow.id)
    assert exc.value.status_code == 404
    assert exc.value.detail == "Borrow record not found or already returned"


def test_get_member_borrows(db_session: Session):
    """Test retrieving all borrowed books for a member."""
    book1 = Book(title="1984", author="George Orwell",
                 total_copies=5, available_copies=4)
    book2 = Book(title="Brave New World", author="Aldous Huxley",
                 total_copies=5, available_copies=4)
    member = Member(email="test@example.com", name="Test User",
                    hashed_password="hashed")
    borrow1 = Borrow(book=book1, member=member)
    borrow2 = Borrow(book=book2, member=member)
    db_session.add_all([book1, book2, member, borrow1, borrow2])
    db_session.commit()

    borrows = get_member_borrows(db_session, member.id)
    assert len(borrows) == 2
    assert borrows[0].book_id in [book1.id, book2.id]
    assert borrows[1].book_id in [book1.id, book2.id]
