"""HotelBook Gateway Service - Reverse proxy to backend services."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.proxy import router

app = FastAPI(title="HotelBook Gateway", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "gateway"}
