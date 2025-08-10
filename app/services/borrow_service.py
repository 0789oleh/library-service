from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.book import Book
from app.models.borrow import Borrow
from app.models.member import Member
from app.schemas.borrow import BorrowCreate
from app.tasks.email_tasks import send_borrow_email, send_return_email
from datetime import datetime


async def borrow_book(borrow_data: BorrowCreate, db: Session) -> Borrow:
    """Borrow a book."""
    book = db.query(Book).filter(Book.id == borrow_data.book_id).first()
    member = db.query(Member).filter(Member.id == borrow_data.member_id).first()
    if not book or not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book or member not found")
    if book.available_copies <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No copies available")
    borrow = Borrow(book_id=borrow_data.book_id, member_id=borrow_data.member_id, notification_sent=False)
    book.available_copies -= 1
    db.add(borrow)
    db.commit()
    db.refresh(borrow)
    send_borrow_email.delay(borrow.id)
    return borrow


async def return_book(borrow_id: int, db: Session) -> Borrow:
    """Return a book."""
    borrow = db.query(Borrow).filter(Borrow.id == borrow_id).first()
    if not borrow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Borrow not found")
    if borrow.return_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book already returned")
    book = db.query(Book).filter(Book.id == borrow.book_id).first()
    book.available_copies += 1
    borrow.return_date = datetime.utcnow()
    borrow.notification_sent = True
    db.commit()
    db.refresh(borrow)
    send_return_email.delay(borrow.id)
    return borrow


async def get_member_borrows(member_id: int, db: Session) -> list[Borrow]:
    """Retrieve a member's borrows."""
    return db.query(Borrow).filter(Borrow.member_id == member_id).all()
