from pydantic import BaseModel, Field, field_validator


class BookBase(BaseModel):
    """Base schema for book-related operations."""
    title: str = Field(..., description="Title of the book", max_length=255)
    author: str = Field(..., description="Author of the book", max_length=100)
    total_copies: int = Field(..., description="Total number of copies", ge=1)

    @field_validator("total_copies")
    def validate_copies(cls, value):
        if value < 1:
            raise ValueError("Total copies must be at least 1")
        return value


class BookCreate(BookBase):
    """Schema for creating a new book."""
    pass


class BookResponse(BookBase):
    """Schema for returning book details."""
    id: int
    available_copies: int = Field(...,
                                  description="Number of available copies",
                                  ge=0)

    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy integration
