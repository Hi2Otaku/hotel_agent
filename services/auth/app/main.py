"""HotelBook Auth Service - Main application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import async_session_factory, engine
from app.api.v1.auth import router as auth_router
from app.api.v1.invite import router as invite_router
from app.api.v1.users import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: seed first admin on startup, dispose engine on shutdown."""
    from app.services.user import get_or_create_admin
    from app.services.seed_guests import seed_demo_guests

    async with async_session_factory() as session:
        admin = await get_or_create_admin(
            session, settings.FIRST_ADMIN_EMAIL, settings.FIRST_ADMIN_PASSWORD
        )
        print(f"Admin ready: {admin.email}")

    # Seed demo guest accounts (separate session)
    try:
        async with async_session_factory() as session:
            await seed_demo_guests(session)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("Guest seed failed: %s", e)

    yield

    # Shutdown: dispose database engine
    await engine.dispose()


app = FastAPI(
    title="HotelBook Auth Service",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware (permissive for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth_router)
app.include_router(invite_router)
app.include_router(users_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "auth"}
