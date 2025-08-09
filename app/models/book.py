from sqlalchemy import Column, Integer, String
from app.models.base import AbstractBase
from sqlalchemy.orm import relationship


class Book(AbstractBase):
    __tablename__ = "books"
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    total_copies = Column(Integer, nullable=False)
    available_copies = Column(Integer, nullable=False)
    borrows = relationship("Borrow", back_populates="book")

    class Config:
        from_attributes = True
