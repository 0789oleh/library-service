from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.base import get_db
from app.models.member import Member
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.member import MemberCreate, MemberResponse
from app.services.auth_service import login_member

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    """Log in a member and return a JWT token."""
    return await login_member(db, login_request)


@router.post("/register", response_model=MemberResponse)
async def register_member(member: MemberCreate, db: Session = Depends(get_db)):
    try:
        # Check if email already exists
        existing_member = db.query(Member)\
            .filter(Member.email == member.email).first()
        if existing_member:
            raise HTTPException(status_code=400,
                                detail="Email already registered")

        # Create new member
        db_member = Member(name=member.name, email=member.email)
        db_member.set_password(member.password)
        db.add(db_member)
        db.commit()
        db.refresh(db_member)
        return db_member
    except Exception as e:
        print(f"Register endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
