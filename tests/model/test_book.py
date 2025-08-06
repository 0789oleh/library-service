import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models.book import Book
from app.models.borrow import Borrow
from app.models.member import Member


def test_create_book(db_session: Session):
    """Test creating a book with valid data."""
    book = Book(
        title="The Great Gatsby",
        author="F. Scott Fitzgerald",
        total_copies=10,
        available_copies=10
    )
    db_session.add(book)
    db_session.commit()

    assert book.id is not None
    assert book.title == "The Great Gatsby"
    assert book.author == "F. Scott Fitzgerald"
    assert book.total_copies == 10
    assert book.available_copies == 10
    assert book.created_at is not None
    assert book.updated_at is not None


def test_book_nullable_constraints(db_session: Session):
    """Test that title and author cannot be null."""
    book = Book(total_copies=5, available_copies=5)
    db_session.add(book)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_book_relationship(db_session: Session):
    """Test the relationship between Book and Borrow."""
    book = Book(
        title="1984",
        author="George Orwell",
        total_copies=5,
        available_copies=5
    )
    member = Member(
        email="test@example.com",
        name="Test User",
        hashed_password="hashed_password"
    )
    borrow = Borrow(book=book, member=member)
    db_session.add_all([book, member, borrow])
    db_session.commit()

    assert len(book.borrows) == 1
    assert book.borrows[0].book_id == book.id
