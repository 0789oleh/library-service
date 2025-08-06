from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Schema for user login."""
    email: str = Field(..., description="Member's email address")
    password: str = Field(..., description="Member's password")


class TokenResponse(BaseModel):
    """Schema for returning JWT token."""
    access_token: str
    token_type: str = "bearer"
