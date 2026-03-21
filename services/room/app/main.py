"""HotelBook Room Service -- FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler. Future: seed data on startup."""
    yield


app = FastAPI(
    title="HotelBook Room Service",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "room"}
