from pydantic import BaseModel, ConfigDict
from typing import Optional


class MemberCreate(BaseModel):
    name: str
    email: str
    password: str
    is_admin: Optional[bool] = False
    model_config = ConfigDict(from_attributes=True)


class MemberResponse(BaseModel):
    id: int
    name: str
    email: str

    model_config = ConfigDict(
        from_attributes=True  # Enable ORM mode for SQLAlchemy integration
    )
