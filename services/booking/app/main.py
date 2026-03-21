"""HotelBook Booking Service -- 3-step booking flow with payment and events."""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.bookings import router as bookings_router
from app.api.v1.staff import router as staff_router
from app.services.expiry import expire_pending_bookings


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Application lifespan: start background expiry task for PENDING bookings."""
    task = asyncio.create_task(expire_pending_bookings())
    yield
    task.cancel()


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

app.include_router(staff_router)       # Staff routes before guest routes for path precedence
app.include_router(bookings_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "booking"}
