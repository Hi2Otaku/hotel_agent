"""HotelBook Room Service -- FastAPI application entry point."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.room_types import router as room_types_router
from app.api.v1.rooms import router as rooms_router
from app.api.v1.rates import router as rates_router
from app.services.event_consumer import start_event_consumer

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler: MinIO bucket init + seed data + event consumer."""
    # MinIO bucket
    try:
        from app.core.storage import get_minio_client
        from app.services.storage import ensure_bucket
        from app.core.config import settings

        client = get_minio_client()
        ensure_bucket(client, settings.MINIO_BUCKET)
    except Exception as e:
        logger.warning(f"MinIO bucket init failed: {e}")

    # Seed data
    from app.core.config import settings

    if settings.SEED_ON_STARTUP:
        from app.core.database import async_session_factory
        from app.services.seed import seed_data

        async with async_session_factory() as session:
            await seed_data(session)

    # Start RabbitMQ event consumer for booking projections
    consumer_task = None
    try:
        consumer_task = asyncio.create_task(start_event_consumer())
    except Exception as e:
        logger.warning(f"RabbitMQ consumer failed to start: {e}")

    yield

    # Graceful shutdown of event consumer
    if consumer_task is not None:
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="HotelBook Room Service",
    version="1.0.0",
    lifespan=lifespan,
)

# Mount routers -- room_types first so /api/v1/rooms/types matches before /api/v1/rooms/{room_id}
app.include_router(room_types_router)
app.include_router(rooms_router)
app.include_router(rates_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "room"}
