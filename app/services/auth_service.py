import logging
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.member import Member
from app.schemas.auth import LoginRequest, TokenResponse
from jose import jwt
from app.core.config import settings
from datetime import datetime, timedelta

from app.schemas.member import MemberCreate


logger = logging.getLogger(__name__)


async def authenticate_member(db: Session, email: str,
                              password: str) -> Member:
    """Authenticate a member by email and password."""
    member = db.query(Member).filter(Member.email == email).first()
    if not member or not member.verify_password(password):
        return None
    return member


async def create_access_token(data: dict) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY,
                             algorithm="HS256")
    return encoded_jwt


async def login_member(login_request: LoginRequest,
                       db: Session = Depends()) -> TokenResponse:
    """Log in a member and return a JWT token."""
    member = await authenticate_member(db, login_request.email,
                                       login_request.password)
    if not member:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": member.email})
    return TokenResponse(access_token=access_token, token_type="bearer")


async def register_member(member: MemberCreate,
                          db: Session = Depends()) -> Member:
    try:
        existing_member = db.query(Member)\
            .filter(Member.email == member.email).first()
        if existing_member:
            raise HTTPException(status_code=400,
                                detail="Email already registered")
        db_member = Member(name=member.name, email=member.email)
        db_member.set_password(member.password)
        db.add(db_member)
        db.commit()
        db.refresh(db_member)
        logger.info(f"Registered member: {member.email}")
        return db_member
    except Exception as e:
        logger.error(f"Register endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
