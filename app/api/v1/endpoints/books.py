from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.book import Book
from app.schemas.book import BookCreate, BookResponse
from app.models.base import get_db
from app.core.security import get_current_admin_user
from app.models.member import Member

router = APIRouter(prefix="/api/v1", tags=["books"])


@router.post("/books", response_model=BookResponse, status_code=201)
async def create_book(
    book_data: BookCreate,
    db: Session = Depends(get_db),
    current_user: Member = Depends(get_current_admin_user)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can create books."
        )
    """Create a new book (admin only)."""
    book = Book(**book_data.dict())
    db.add(book)
    db.commit()
    db.refresh(book)
    return BookResponse.model_validate(book)
