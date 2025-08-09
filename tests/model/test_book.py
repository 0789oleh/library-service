import pytest
from sqlalchemy.orm import Session
from app.models.book import Book
from app.models.member import Member
from app.models.borrow import Borrow
from sqlalchemy.exc import IntegrityError


def test_create_book(db_session: Session):
    """Test creating a book."""
    book = Book(
        title="1984",
        author="George Orwell",
        total_copies=5,
        available_copies=5
    )
    db_session.add(book)
    db_session.commit()
    assert book.id is not None
    db_session.rollback()  # Ensure clean session


def test_book_nullable_constraints(db_session: Session):
    """Test that title and author are not nullable."""
    book = Book(
        title=None,  # Invalid: title is NOT NULL
        author=None,  # Invalid: author is NOT NULL
        total_copies=5,
        available_copies=5
    )
    db_session.add(book)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()  # Ensure clean session


def test_book_relationship(db_session: Session):
    """Test the relationship between Book and Borrow."""
    book = Book(
        title="1984",
        author="George Orwell",
        total_copies=5,
        available_copies=5
    )
    member = Member(
        email="unique_book@example.com",
        name="Test User",
        hashed_password="hashed_password"
    )
    borrow = Borrow(book=book, member=member)
    db_session.add_all([book, member, borrow])
    db_session.commit()
    assert book.borrows == [borrow]
    db_session.rollback()  # Ensure clean session
