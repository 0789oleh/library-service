from fastapi import FastAPI
from app.models.base import get_engine, Base
from app.api.v1.endpoints.borrow import router as borrow_router
from app.api.v1.endpoints.auth import router as auth_router
import logging

logger = logging.getLogger(__name__)

app = FastAPI()

logger.info("Including borrow_router")
app.include_router(borrow_router, prefix="/api/v1")
logger.info("Including auth_router")
app.include_router(auth_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    try:
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise


@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Library Management System"}
