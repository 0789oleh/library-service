import pytest
from sqlalchemy.orm import Session
from app.services.auth_service import create_access_token, authenticate_member, login_member
from app.models.member import Member
from app.schemas.auth import LoginRequest, TokenResponse
from app.core.config import settings
from jose import jwt
from fastapi import HTTPException
from datetime import datetime
import os


@pytest.fixture
def set_test_db():
    """Set TEST_DATABASE_URL for in-memory SQLite."""
    os.environ["TEST_DATABASE_URL"] = "sqlite:///:memory:"
    yield
    os.environ.pop("TEST_DATABASE_URL", None)


@pytest.mark.asyncio
async def test_create_access_token():
    """Test JWT token creation."""
    data = {"sub": "test@example.com"}
    token = create_access_token(data)
    decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
    assert decoded["sub"] == "test@example.com"
    assert "exp" in decoded


@pytest.mark.asyncio
async def test_authenticate_member_success(db_session: Session, set_test_db):
    """Test successful member authentication."""
    unique_email = f"auth_success_{int(datetime.utcnow().timestamp())}@example.com"
    member = Member(email=unique_email, name="Test User")
    member.set_password("testpassword")
    db_session.add(member)
    db_session.commit()
    authenticated_member = await authenticate_member(db_session, unique_email, "testpassword")
    assert authenticated_member.email == unique_email
    db_session.rollback()


@pytest.mark.asyncio
async def test_authenticate_member_invalid(db_session: Session, set_test_db):
    """Test authentication with invalid credentials."""
    unique_email = f"auth_invalid_{int(datetime.utcnow().timestamp())}@example.com"
    member = Member(email=unique_email, name="Test User")
    member.set_password("testpassword")
    db_session.add(member)
    db_session.commit()
    authenticated_member = await authenticate_member(db_session, unique_email, "wrongpassword")
    assert authenticated_member is None
    authenticated_member = await authenticate_member(db_session, "nonexistent@example.com", "testpassword")
    assert authenticated_member is None
    db_session.rollback()


@pytest.mark.asyncio
async def test_login_member(db_session: Session, set_test_db):
    """Test member login with valid credentials."""
    unique_email = f"login_member_{int(datetime.utcnow().timestamp())}@example.com"
    member = Member(email=unique_email, name="Test User")
    member.set_password("testpassword")
    db_session.add(member)
    db_session.commit()
    login_request = LoginRequest(email=unique_email, password="testpassword")
    token_response = await login_member(login_request, db_session)
    assert isinstance(token_response, TokenResponse)
    assert token_response.token_type == "bearer"
    assert token_response.access_token
    decoded = jwt.decode(token_response.access_token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
    assert decoded["sub"] == unique_email
    db_session.rollback()


@pytest.mark.asyncio
async def test_login_member_invalid(db_session: Session, set_test_db):
    """Test member login with invalid credentials."""
    unique_email = f"login_invalid_{int(datetime.utcnow().timestamp())}@example.com"
    member = Member(email=unique_email, name="Test User")
    member.set_password("testpassword")
    db_session.add(member)
    db_session.commit()
    login_request = LoginRequest(email=unique_email, password="wrongpassword")
    with pytest.raises(HTTPException) as exc:
        await login_member(login_request, db_session)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid credentials"
    login_request = LoginRequest(email="nonexistent@example.com", password="testpassword")
    with pytest.raises(HTTPException) as exc:
        await login_member(login_request, db_session)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid credentials"
    db_session.rollback()
