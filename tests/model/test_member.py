import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models.member import Member
from app.models.borrow import Borrow
from app.models.book import Book


async def test_create_member(db_session: Session):
    """Test creating a member with valid data."""
    member = Member(
        email="user@example.com",
        name="John Doe",
        hashed_password="hashed_password"
    )
    db_session.add(member)
    db_session.commit()

    assert member.id is not None
    assert member.email == "user@example.com"
    assert member.name == "John Doe"
    assert member.hashed_password == "hashed_password"
    assert member.created_at is not None
    assert member.updated_at is not None


async def test_member_unique_email(db_session: Session):
    """Test that email must be unique."""
    member1 = Member(
        email="user@example.com",
        name="John Doe",
        hashed_password="hashed_password"
    )
    member2 = Member(
        email="user@example.com",
        name="Jane Doe",
        hashed_password="different_password"
    )
    db_session.add(member1)
    db_session.commit()
    db_session.add(member2)
    with pytest.raises(IntegrityError):
        db_session.commit()


async def test_member_relationship(db_session: Session):
    """Test the relationship between Member and Borrow."""
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

    assert len(member.borrows) == 1
    assert member.borrows[0].member_id == member.id
