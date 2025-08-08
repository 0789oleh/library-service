from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.base import get_db
from app.schemas.borrow import BorrowRequest, BorrowResponse
from app.services.borrow_service import borrow_book, return_book, \
    get_member_borrows
from app.core.security import get_current_member
from app.models.member import Member
from typing import List

router = APIRouter()


@router.post("/", response_model=BorrowResponse)
async def borrow_book_endpoint(
    request: BorrowRequest,
    db: Session = Depends(get_db),
    current_member: Member = Depends(get_current_member)
):
    """Borrow a book (v2, with email notification)."""
    borrow = borrow_book(db, request.book_id,
                         request.member_id, api_version="v1")
    return borrow


@router.post("/{borrow_id}/return", response_model=BorrowResponse)
async def return_book_endpoint(
    borrow_id: int,
    db: Session = Depends(get_db),
    current_member: Member = Depends(get_current_member)
):
    """Return a book (v2, with email notification)."""
    borrow = return_book(db, borrow_id, api_version="v1")
    return borrow


@router.get("/member/{member_id}", response_model=List[BorrowResponse])
def get_member_borrows_endpoint(
    member_id: int,
    db: Session = Depends(get_db),
    current_member: Member = Depends(get_current_member)
):
    """Get all borrowed books for a member."""
    return get_member_borrows(db, member_id)
