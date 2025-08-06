from fastapi import FastAPI
from app.models.base import get_engine
from app.api.v1.router import router as v1_router
from app.api.v2.router import router as v2_router

app = FastAPI(title="Library Management System")


# Initialize database tables
@app.on_event("startup")
def on_startup():
    get_engine()


app.include_router(v1_router, prefix="/v1")
app.include_router(v2_router, prefix="/v2")
