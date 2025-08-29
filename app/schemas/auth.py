from pydantic import BaseModel, ConfigDict


class LoginRequest(BaseModel):
    email: str
    password: str
    model_config = ConfigDict(
        from_attributes=True  # Enable ORM mode for SQLAlchemy integration
    )


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    model_config = ConfigDict(
        from_attributes=True  # Enable ORM mode for SQLAlchemy integration
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    model_config = ConfigDict(
        from_attributes=True  # Enable ORM mode for SQLAlchemy integration
    )


class Token(BaseModel):
    access_token: str
    token_type: str
    model_config = ConfigDict(from_attributes=True)
