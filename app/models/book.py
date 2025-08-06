from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import AbstractBase


class Book(AbstractBase):
    """Represents a book in the library."""
    __tablename__ = "books"

    title = Column(String(255), nullable=False,
                   index=True, doc="Title of the book")
    author = Column(String(100), nullable=False, doc="Author of the book")
    total_copies = Column(Integer, nullable=False,
                          doc="Total number of copies")
    available_copies = Column(Integer, nullable=False,
                              doc="Number of available copies")

    borrows = relationship("Borrow", back_populates="book")
