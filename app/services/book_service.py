from sqlalchemy.orm import Session
from app.models.book import Book
from app.schemas.book import BookCreate, BookResponse
from fastapi import HTTPException, status


async def create_book(db: Session, book_data: BookCreate) -> BookResponse:
    """Create a new book in the library."""
    book = Book(
        title=book_data.title,
        author=book_data.author,
        total_copies=book_data.total_copies,
        available_copies=book_data.available_copies
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return BookResponse.model_validate(book)


async def get_book(db: Session, book_id: int) -> BookResponse:
    """Retrieve a book by ID."""
    book = await db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return await BookResponse.model_validate(book)
