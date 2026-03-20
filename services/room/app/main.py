"""HotelBook Room Service - Stub for Phase 1."""

from fastapi import FastAPI

app = FastAPI(title="HotelBook Room Service", version="1.0.0")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "room"}
