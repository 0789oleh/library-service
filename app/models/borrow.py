from sqlalchemy import Boolean, Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import AbstractBase


class Borrow(AbstractBase):
    __tablename__ = "borrows"
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    notification_sent = Column(Boolean, default=False)
    return_date = Column(DateTime, nullable=True)
    book = relationship("Book", back_populates="borrows")
    member = relationship("Member", back_populates="borrows")
