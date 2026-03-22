"""Chat service database configuration.

Uses shared library for engine and session factory creation.
Re-exports Base for model inheritance.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import Base, create_db_engine, create_session_factory
from app.core.config import settings

engine = create_db_engine(settings.DATABASE_URL, echo=settings.DEBUG)
async_session_factory = create_session_factory(engine)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session for FastAPI dependency injection."""
    async with async_session_factory() as session:
        yield session


__all__ = ["Base", "engine", "async_session_factory", "get_session"]
