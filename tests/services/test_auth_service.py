from sqlalchemy.orm import Session
from app.services.auth_service import create_access_token, authenticate_member, login_member
from app.models.member import Member
from app.schemas.auth import LoginRequest, TokenResponse
from app.core.config import settings
from jose import jwt
from fastapi import HTTPException


async def test_create_access_token():
    """Test JWT token creation."""
    data = {"sub": "test@example.com"}
    token = create_access_token(data)
    decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
    assert decoded["sub"] == "test@example.com"
    assert "exp" in decoded


async def test_authenticate_member_success(db_session: Session):
    """Test successful member authentication."""
    member = Member(email="test@example.com", name="Test User")
    member.set_password("testpassword")
    db_session.add(member)
    db_session.commit()

    authenticated_member = await authenticate_member(db_session, "test@example.com", "testpassword")
    assert authenticated_member.email == "test@example.com"


async def test_authenticate_member_invalid(db_session: Session):
    """Test authentication with invalid credentials."""
    member = Member(email="test@example.com", name="Test User")
    member.set_password("testpassword")
    db_session.add(member)
    db_session.commit()

    authenticated_member = await authenticate_member(db_session, "test@example.com", "wrongpassword")
    assert authenticated_member is None

    authenticated_member = await authenticate_member(db_session, "nonexistent@example.com", "testpassword")
    assert authenticated_member is None


async def test_login_member(db_session: Session):
    """Test member login with valid credentials."""
    member = Member(email="test@example.com", name="Test User")
    member.set_password("testpassword")
    db_session.add(member)
    db_session.commit()

    login_request = LoginRequest(email="test@example.com", password="testpassword")
    token_response = await login_member(login_request, db_session)
    assert isinstance(token_response, TokenResponse)
    assert token_response.token_type == "bearer"
    assert token_response.access_token


async def test_login_member_invalid(db_session: Session):
    """Test member login with invalid credentials."""
    member = Member(email="test@example.com", name="Test User")
    member.set_password("testpassword")
    db_session.add(member)
    db_session.commit()

    login_request = LoginRequest(email="test@example.com", password="wrongpassword")
    with pytest.raises(HTTPException) as exc:
        await login_member(login_request, db_session)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid credentials"

    login_request = LoginRequest(email="nonexistent@example.com", password="testpassword")
    with pytest.raises(HTTPException) as exc:
        await login_member(login_request, db_session)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid credentials"