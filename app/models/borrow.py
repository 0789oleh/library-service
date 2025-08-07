from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import AbstractBase
from datetime import datetime


class Borrow(AbstractBase):
    __tablename__ = "borrows"
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    borrow_date = Column(DateTime, nullable=False, default=datetime.now)
    return_date = Column(DateTime, nullable=True)
    member = relationship("Member", back_populates="borrows")
    book = relationship("Book", back_populates="borrows")

    class Config:
        from_attributes = True
