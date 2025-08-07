from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.book import Book
from app.models.member import Member
from app.models.borrow import Borrow
from app.schemas.borrow import BorrowResponse
from datetime import datetime
from typing import List


async def borrow_book(db: Session, book_id: int, member_id: int,
                      api_version: str = "v1") -> BorrowResponse:
    """Borrow a book, reducing available copies."""
    book = db.query(Book).filter(Book.id == book_id).first()
    member = db.query(Member).filter(Member.id == member_id).first()

    if not book or not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Book or member not found")
    if book.available_copies < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No copies available")

    book.available_copies -= 1
    borrow = Borrow(
        book_id=book_id,
        member_id=member_id,
        notification_sent=(api_version == "v2")
    )
    db.add(borrow)
    db.commit()
    db.refresh(borrow)
    return await BorrowResponse.from_orm(borrow)


async def return_book(db: Session, borrow_id: int, api_version: str = "v1") \
      -> BorrowResponse:
    """Return a book, increasing available copies."""
    borrow = db.query(Borrow).filter(Borrow.id == borrow_id,
                                     Borrow.return_date.is_(None)).first()
    if not borrow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='''Borrow record
                            not found or already returned''')

    book = db.query(Book).filter(Book.id == borrow.book_id).first()
    book.available_copies += 1
    borrow.return_date = datetime.utcnow()
    borrow.notification_sent = (api_version == "v2")
    db.commit()
    db.refresh(borrow)
    return await BorrowResponse.from_orm(borrow)


async def get_member_borrows(db: Session,
                             member_id: int) -> List[BorrowResponse]:
    """Retrieve all borrowed books for a member."""
    borrows = db.query(Borrow) \
        .filter(Borrow.member_id == member_id, Borrow.return_date.is_(None)) \
        .all()
    return await [BorrowResponse.from_orm(borrow) for borrow in borrows]
