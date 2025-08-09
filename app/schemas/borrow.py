from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class BorrowRequest(BaseModel):
    """Schema for borrowing a book."""
    book_id: int = Field(..., description="ID of the book to borrow")
    member_id: int = Field(..., description="ID of the borrowing member")
    model_config = ConfigDict(
        from_attributes=True  # Enable ORM mode for SQLAlchemy integration
    )


class BorrowResponse(BaseModel):
    """Schema for returning borrow details."""
    id: int
    book_id: int
    member_id: int
    borrow_date: datetime
    return_date: Optional[datetime] = Field(None,
                                            description='''Date the book
                                            was returned''')
    # v2-specific: Include additional fields if needed
    notification_sent: Optional[bool] = Field(None,
                                              description='''Whether
                                              email notification
                                              was sent (v2 only)''')
    model_config = ConfigDict(
        from_attributes=True  # Enable ORM mode for SQLAlchemy integration
    )


class BorrowCreate(BaseModel):
    """Schema for creating a new borrow record."""
    book_id: int = Field(..., description="ID of the book to borrow")
    member_id: int = Field(..., description="ID of the borrowing member")
    notification_sent: Optional[bool] = Field(
        False, description="Whether to send a notification (v2 only)"
    )
    model_config = ConfigDict(
        from_attributes=True  # Enable ORM mode for SQLAlchemy integration
    )
