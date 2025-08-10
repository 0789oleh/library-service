import pytest
from sqlalchemy.orm import Session
from app.services.book_service import create_book, get_book
from app.schemas.book import BookCreate
from app.models.book import Book
from fastapi import HTTPException
import os


@pytest.fixture
def set_test_db():
    """Set TEST_DATABASE_URL for in-memory SQLite."""
    os.environ["TEST_DATABASE_URL"] = "sqlite:///:memory:"
    yield
    os.environ.pop("TEST_DATABASE_URL", None)


@pytest.mark.asyncio
async def test_create_book(db_session: Session, set_test_db):
    """Test creating a book."""
    book_data = BookCreate(title="1984", author="George Orwell", total_copies=5)
    book = await create_book(db_session, book_data)
    assert book.id is not None
    assert book.title == "1984"
    db_session.rollback()


@pytest.mark.asyncio
async def test_get_book_success(db_session: Session, set_test_db):
    """Test retrieving a book by ID."""
    book = Book(title="1984", author="George Orwell", total_copies=5, available_copies=5)
    db_session.add(book)
    db_session.commit()
    retrieved_book = get_book(db_session, book.id)
    assert retrieved_book.id == book.id
    assert retrieved_book.title == "1984"
    db_session.rollback()


@pytest.mark.asyncio
async def test_get_book_not_found(db_session: Session, set_test_db):
    """Test retrieving a non-existent book."""
    with pytest.raises(HTTPException) as exc:
        await get_book(db_session, 999)
    assert exc.value.status_code == 404
    assert exc.value.detail == "Book not found"
    db_session.rollback()
