from pydantic_settings import BaseSettings
from pydantic import ValidationError


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    DATABASE_URL: str
    REDIS_URL: str
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    JWT_SECRET_KEY: str
    JWT_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print(f"Loaded DATABASE_URL: {self.DATABASE_URL}")
        if "library_db" not in self.DATABASE_URL:
            raise ValueError(f"""Invalid DATABASE_URL: {self.DATABASE_URL},
                              expected 'library_db'""")


def get_settings() -> Settings:
    """Lazily instantiate Settings to avoid import-time errors."""
    try:
        return Settings()
    except ValidationError as e:
        print(f"Settings validation error: {e}")
        raise


settings = get_settings()
