"""Shared database utilities for all services.

Provides async engine creation, session factory, and a common
declarative base for SQLAlchemy models.
"""

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Common declarative base for all service models."""

    pass


def create_db_engine(database_url: str, echo: bool = False) -> AsyncEngine:
    """Create an async SQLAlchemy engine.

    Args:
        database_url: PostgreSQL async connection URL
            (e.g., postgresql+asyncpg://user:pass@host:5432/db).
        echo: Whether to log SQL statements.

    Returns:
        An async engine with connection pooling configured.
    """
    return create_async_engine(
        database_url,
        echo=echo,
        pool_size=5,
        max_overflow=10,
    )


def create_session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """Create an async session factory.

    Args:
        engine: The async engine to bind sessions to.

    Returns:
        A session factory that produces AsyncSession instances.
    """
    return async_sessionmaker(engine, expire_on_commit=False)


__all__ = ["Base", "create_db_engine", "create_session_factory"]
