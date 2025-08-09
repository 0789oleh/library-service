from pydantic import BaseModel, ConfigDict


class MemberCreate(BaseModel):
    name: str
    email: str
    password: str
    model_config = ConfigDict(from_attributes=True)


class MemberResponse(BaseModel):
    id: int
    name: str
    email: str

    model_config = ConfigDict(
        from_attributes=True  # Enable ORM mode for SQLAlchemy integration
    )
