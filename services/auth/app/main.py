"""HotelBook Auth Service - Main application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.core.config import settings
from app.core.database import async_session_factory, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: seed first admin on startup, dispose engine on shutdown."""
    # Startup: seed first admin user
    from app.models.user import User, UserRole
    from app.core.security import hash_password

    async with async_session_factory() as session:
        result = await session.execute(
            select(User).where(User.email == settings.FIRST_ADMIN_EMAIL)
        )
        existing_admin = result.scalar_one_or_none()
        if not existing_admin:
            admin = User(
                email=settings.FIRST_ADMIN_EMAIL,
                password_hash=hash_password(settings.FIRST_ADMIN_PASSWORD),
                first_name="Admin",
                last_name="User",
                role=UserRole.ADMIN,
                is_active=True,
            )
            session.add(admin)
            await session.commit()
            print(f"First admin created: {settings.FIRST_ADMIN_EMAIL}")
        else:
            print(f"Admin already exists: {settings.FIRST_ADMIN_EMAIL}")

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


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "auth"}
