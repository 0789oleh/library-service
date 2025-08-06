from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.base import get_db
from app.schemas.book import BookCreate, BookResponse
from app.services.book_service import create_book

router = APIRouter()


@router.post("/", response_model=BookResponse)
async def create_book_endpoint(book_data: BookCreate,
                               db: Session = Depends(get_db)):
    """Register a new book in the library."""
    return await create_book(db, book_data)
