from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.config import settings
from app.models.member import Member
from app.schemas.auth import LoginRequest, TokenResponse


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return await pwd_context.verify(plain_password, hashed_password)


async def get_password_hash(password: str) -> str:
    """Hash a password for storage."""
    return await pwd_context.hash(password)


async def create_access_token(data: dict) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY,
                             algorithm="HS256")
    return await encoded_jwt


async def authenticate_member(db: Session, email: str,
                              password: str) -> Member:
    """Authenticate a member by email and password."""
    member = db.query(Member).filter(Member.email == email).first()
    if not member or not verify_password(password, member.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return member


async def login_member(db: Session,
                       login_request: LoginRequest) -> TokenResponse:
    """Log in a member and return a JWT token."""
    member = authenticate_member(db, login_request.email,
                                 login_request.password)
    access_token = create_access_token(data={"sub": member.email})
    return await TokenResponse(access_token=access_token, token_type="bearer")
