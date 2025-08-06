from pydantic import BaseModel, EmailStr, Field


class MemberBase(BaseModel):
    """Base schema for member-related operations."""
    email: EmailStr = Field(..., description="Member's email address")
    name: str = Field(..., description="Member's full name", max_length=100)


class MemberCreate(MemberBase):
    """Schema for creating a new member."""
    password: str = Field(..., description="Member's password", min_length=8)


class MemberResponse(MemberBase):
    """Schema for returning member details."""
    id: int

    class Config:
        orm_mode = True  # Enable ORM mode for SQLAlchemy integration