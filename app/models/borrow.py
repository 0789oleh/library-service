from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.base import AbstractBase


class Borrow(AbstractBase):
    """Represents a book borrowing record."""
    __tablename__ = "borrows"

    book_id = Column(Integer, ForeignKey("books.id"), nullable=False,
                     doc="ID of the borrowed book")
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False,
                       doc="ID of the borrowing member")
    notification_sent = Column(Boolean, default=False,
                               doc='''Whether email notification
                                 was sent (v2 only)''')

    book = relationship("Book", back_populates="borrows")
    member = relationship("Member", back_populates="borrows")
