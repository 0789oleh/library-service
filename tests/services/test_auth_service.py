import pytest
from sqlalchemy.orm import Session
from app.services.auth_service import verify_password, \
    get_password_hash, create_access_token, authenticate_member, login_member
from app.models.member import Member
from app.schemas.auth import LoginRequest, TokenResponse
from fastapi import HTTPException
from jose import jwt


def test_get_password_hash():
    """Test password hashing."""
    password = "testpassword"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)


def test_verify_password():
    """Test password verification."""
    password = "testpassword"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_create_access_token():
    """Test JWT token creation."""
    data = {"sub": "test@example.com"}
    token = create_access_token(data)
    decoded = jwt.decode(token, "secret", algorithms=["HS256"])
    assert decoded["sub"] == "test@example.com"
    assert "exp" in decoded


def test_authenticate_member_success(db_session: Session):
    """Test successful member authentication."""
    hashed_password = get_password_hash("testpassword")
    member = Member(email="test@example.com", name="Test User",
                    hashed_password=hashed_password)
    db_session.add(member)
    db_session.commit()

    authenticated_member = authenticate_member(db_session, "test@example.com",
                                               "testpassword")
    assert authenticated_member.email == "test@example.com"


def test_authenticate_member_invalid(db_session: Session):
    """Test authentication with invalid credentials."""
    hashed_password = get_password_hash("testpassword")
    member = Member(email="test@example.com", name="Test User",
                    hashed_password=hashed_password)
    db_session.add(member)
    db_session.commit()

    with pytest.raises(HTTPException) as exc:
        authenticate_member(db_session, "test@example.com", "wrongpassword")
    assert exc.value.status_code == 401


def test_login_member(db_session: Session):
    """Test member login with valid credentials."""
    hashed_password = get_password_hash("testpassword")
    member = Member(email="test@example.com", name="Test User",
                    hashed_password=hashed_password)
    db_session.add(member)
    db_session.commit()

    login_request = LoginRequest(email="test@example.com",
                                 password="testpassword")
    token_response = login_member(db_session, login_request)
    assert isinstance(token_response, TokenResponse)
    assert token_response.token_type == "bearer"
    assert token_response.access_token
