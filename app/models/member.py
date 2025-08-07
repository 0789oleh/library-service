from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.models.base import AbstractBase
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Member(AbstractBase):
    __tablename__ = "members"
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    borrows = relationship("Borrow", back_populates="member")

    def set_password(self, password: str):
        self.hashed_password = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)

    class Config:
        from_attributes = True
