from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import hashlib

from app.models.base import AbstractBase


class Member(AbstractBase):
    """Represents a library member."""
    __tablename__ = "members"

    email = Column(String(255), unique=True, nullable=False,
                   index=True, doc="Member's email address")
    name = Column(String(100), nullable=False, doc="Member's full name")
    hashed_password = Column(String(255), nullable=False,
                             doc="Hashed password for authentication")

    borrows = relationship("Borrow", back_populates="member")
