from fastapi import APIRouter
from app.api.v2.endpoints import auth, books, borrow

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(books.router, prefix="/books", tags=["books"])
router.include_router(borrow.router, prefix="/borrow", tags=["borrow"])
