"""FastAPI backend entry point.

Run with:   uvicorn app.main:app --reload
API docs:   http://127.0.0.1:8000/docs   (interactive Swagger UI)

The Streamlit frontend (streamlit_app.py) talks to this API over HTTP.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.ml.predictor import _load_model
from app.routers import patients


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables if they don't exist, and warm up the ML model
    # (trains it automatically on first run if the file is missing).
    Base.metadata.create_all(bind=engine)
    _load_model()
    yield


app = FastAPI(
    title="MIRA Health Prediction API",
    description="CRUD for patient blood test records with AI-generated health remarks.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(patients.router)


@app.get("/", tags=["Health Check"])
def health_check():
    """Simple check that the API is alive - used by the Streamlit frontend."""
    return {"status": "ok", "message": "MIRA Health Prediction API is running"}
