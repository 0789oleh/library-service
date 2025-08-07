from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.models.base import get_engine, Base
from app.api.v1.endpoints.borrow import router as borrow_router
from app.api.v1.endpoints.auth import router as auth_router
import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application."""
    engine = None
    try:
        logger.info("Starting application")
        engine = get_engine()
        # Verify database connection
        with engine.connect() as conn:
            logger.info(f"Database connection established: {conn.engine.url}")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        # Log router inclusion
        logger.info("Included API routers: auth, borrow")
        yield
    except Exception as e:
        logger.error(f"Application startup error: {e}")
        raise
    finally:
        if engine:
            engine.dispose()
            logger.info("Database engine disposed")
        logger.info("Application shutdown complete")

app = FastAPI(
    title="Library Management System",
    description="API for managing library members, books, and borrows",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(borrow_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")


@app.get("/", summary="Root endpoint")
async def root():
    """Return a welcome message for the Library Management System."""
    logger.info("Root endpoint accessed")
    return {"message": "Library Management System"}
