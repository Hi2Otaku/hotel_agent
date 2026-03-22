"""HotelBook Chat Service -- AI-powered chatbot for guest and staff interactions."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Application lifespan: initialize DB engine on startup."""
    yield


app = FastAPI(
    title="HotelBook Chat Service",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "chat"}
