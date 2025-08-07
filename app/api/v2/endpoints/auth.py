import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.base import get_db
from app.models.member import Member
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.member import MemberCreate, MemberResponse
from app.services.auth_service import login_member, register_member


router = APIRouter()


logger = logging.getLogger(__name__)


@router.post("/login", response_model=TokenResponse)
async def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    try:
        return await login_member(login_request, db)
    except HTTPException as e:
        logger.error(f"Login endpoint error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected login error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/register", response_model=MemberResponse)
async def register(member: MemberCreate, db: Session = Depends(get_db)):
    return await register_member(member, db)
