import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module", autouse=True)
def mock_settings():
    with patch("app.core.config.get_settings") as mock_get_settings:
        mock_settings = MagicMock()
        mock_settings.DATABASE_URL = "sqlite:///:memory:"
        mock_settings.REDIS_URL = "redis://localhost:6379/0"
        mock_settings.SMTP_HOST = "smtp.example.com"
        mock_settings.SMTP_PORT = 587
        mock_settings.SMTP_USER = "user@example.com"
        mock_settings.SMTP_PASSWORD = "password"
        mock_settings.JWT_SECRET_KEY = "test-secret-key"
        mock_settings.JWT_EXPIRE_MINUTES = 30
        mock_get_settings.return_value = mock_settings
        yield mock_settings


@pytest.fixture(scope="function")
def db_session():
    """Create an in-memory SQLite session for tests."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        engine.dispose()


@pytest.fixture
def client(db_session):
    """Create a FastAPI test client with overridden DB dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    app.dependency_overrides[app.get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def mock_celery():
    """Mock Celery task calls."""
    with patch("app.tasks.email_tasks.app.task") as mock_task:
        yield mock_task


@pytest.fixture
def mock_smtp():
    """Mock aiosmtplib send function."""
    with patch("aiosmtplib.send", new=AsyncMock()) as mock_send:
        yield mock_send
