from sqlalchemy import Column, Integer, String
from app.models.base import AbstractBase
from sqlalchemy.orm import relationship


class Book(AbstractBase):
    __tablename__ = "books"
    title = Column(String, nullable=False)
    available_copies = Column(Integer, nullable=False)
    borrows = relationship("Borrow", back_populates="book")

    class Config:
        from_attributes = True
