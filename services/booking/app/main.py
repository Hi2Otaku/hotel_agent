"""HotelBook Booking Service -- 3-step booking flow with payment and events."""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.bookings import router as bookings_router
from app.api.v1.reports import router as reports_router
from app.api.v1.staff import router as staff_router
from app.services.expiry import expire_pending_bookings


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Application lifespan: start background expiry task and seed demo data."""
    task = asyncio.create_task(expire_pending_bookings())

    # Seed historical bookings for demo
    try:
        from app.core.database import async_session_factory
        from app.services.seed_bookings import seed_historical_bookings

        async with async_session_factory() as session:
            await seed_historical_bookings(session)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("Booking seed failed: %s", e)

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
app.include_router(reports_router)     # Staff reports after staff routes
app.include_router(bookings_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "booking"}
