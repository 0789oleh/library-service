import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
import urllib.parse
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


def get_engine():
    try:
        settings = get_settings()
        database_url = os.getenv("TEST_DATABASE_URL", settings.DATABASE_URL)
        logger.info(f"Attempting to connect to DATABASE_URL: {database_url}")
        parsed_url = urllib.parse.urlparse(database_url)
        logger.info(f"Parsed DATABASE_URL: scheme={parsed_url.scheme}, host={parsed_url.hostname}, port={parsed_url.port}, path={parsed_url.path}")
        if parsed_url.scheme == "postgresql" and parsed_url.path != "/library_db":
            raise ValueError(f"Invalid database name in DATABASE_URL: {parsed_url.path}, expected '/library_db'")
        connect_args = {"check_same_thread": False} if parsed_url.scheme == "sqlite" else {}
        engine = create_engine(database_url, echo=True, connect_args=connect_args)
        conn = engine.connect()
        logger.info(f"Successfully connected to database: {conn}")
        conn.close()
        return engine
    except Exception as e:
        logger.error(f"Error creating engine: {e}")
        raise


def get_db():
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class AbstractBase(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
