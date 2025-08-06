from sqlalchemy import create_engine, Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from fastapi import Depends
from app.core.config import get_settings


# Create SQLAlchemy declarative base
Base = declarative_base()


def get_engine():
    try:
        settings = get_settings()
        return create_engine(settings.DATABASE_URL)
    except Exception as e:
        print(f"Error creating engine: {e}")
        raise


class AbstractBase(Base):
    """Base class for SQLAlchemy models with common fields."""
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True,
                doc="Unique identifier for the record")
    created_at = Column(DateTime, default=datetime.now,
                        doc="Timestamp when the record was created")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now,
                        doc="Timestamp when the record was last updated")

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"


# Database engine and session setup
engine = create_engine(get_settings().DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency to provide a database session."""
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session(db: SessionLocal = Depends(get_db)):
    """Helper to get the database session for use in services."""
    return db
