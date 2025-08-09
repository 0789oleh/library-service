from sqlalchemy import inspect
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.base import get_db
from app.models.book import Book
from unittest.mock import patch
from app.core.config import settings


def test_abstract_base_fields(db_session: Session):
    """Test that AbstractBase provides id, created_at,
    and updated_at fields."""
    book = Book(
        title="Test Book",
        author="Test Author",
        total_copies=5,
        available_copies=5
    )
    db_session.add(book)
    db_session.commit()

    assert book.id is not None
    assert isinstance(book.created_at, datetime)
    assert isinstance(book.updated_at, datetime)
    assert book.created_at <= book.updated_at


def test_init_db(db_session: Session):
    """Test that init_db creates all tables."""
    inspector = inspect(db_session.bind)
    assert "books" in inspector.get_table_names()
    assert "members" in inspector.get_table_names()
    assert "borrows" in inspector.get_table_names()


def test_get_db_session():
    """Test that get_db yields a valid session."""
    # Get the session from the get_db generator
    db_gen = get_db()
    db = next(db_gen)  # Extract the session
    assert isinstance(db, Session)
    assert db.bind is not None
    # Clean up the generator
    try:
        next(db_gen, None)  # Trigger the finally block to close the session
    except StopIteration:
        pass


def test_updated_at_on_update(db_session: Session):
    """Test that updated_at changes when a record is updated."""
    book = Book(
        title="Test Book",
        author="Test Author",
        total_copies=5,
        available_copies=5
    )
    db_session.add(book)
    db_session.commit()

    original_updated_at = book.updated_at
    book.title = "Updated Book"
    db_session.commit()

    assert book.updated_at > original_updated_at
