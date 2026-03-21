"""HotelBook Booking Service -- 3-step booking flow with payment and events."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.bookings import router as bookings_router


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Application lifespan: placeholder for expiry background task (Plan 03)."""
    yield


app = FastAPI(
    title="HotelBook Booking Service",
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

app.include_router(bookings_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "booking"}
