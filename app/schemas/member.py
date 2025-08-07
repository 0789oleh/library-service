from pydantic import BaseModel


class MemberCreate(BaseModel):
    name: str
    email: str
    password: str


class MemberResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True
