"""Demo guest account seeding for portfolio demo.

Seeds 8 demo guest accounts with @demo.hotelbook.com emails on startup.
Idempotent -- skips if demo guests already exist.
"""

import logging

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)

DEMO_GUESTS = [
    {"first_name": "James", "last_name": "Smith", "email": "james.smith@demo.hotelbook.com"},
    {"first_name": "Emma", "last_name": "Johnson", "email": "emma.johnson@demo.hotelbook.com"},
    {"first_name": "Liam", "last_name": "Williams", "email": "liam.williams@demo.hotelbook.com"},
    {"first_name": "Olivia", "last_name": "Brown", "email": "olivia.brown@demo.hotelbook.com"},
    {"first_name": "Noah", "last_name": "Garcia", "email": "noah.garcia@demo.hotelbook.com"},
    {"first_name": "Ava", "last_name": "Martinez", "email": "ava.martinez@demo.hotelbook.com"},
    {"first_name": "William", "last_name": "Davis", "email": "william.davis@demo.hotelbook.com"},
    {"first_name": "Sophia", "last_name": "Rodriguez", "email": "sophia.rodriguez@demo.hotelbook.com"},
]

DEMO_PASSWORD = "demo123"


async def seed_demo_guests(db: AsyncSession) -> None:
    """Seed demo guest accounts. Idempotent -- skips if any demo guests exist."""
    existing_count = await db.scalar(
        select(func.count()).select_from(User).where(User.email.like("%@demo.hotelbook.com"))
    )
    if existing_count and existing_count > 0:
        logger.info("Demo guests already seeded (%d exist), skipping.", existing_count)
        return

    logger.info("Seeding %d demo guest accounts...", len(DEMO_GUESTS))

    hashed = hash_password(DEMO_PASSWORD)
    guests = [
        User(
            email=g["email"],
            password_hash=hashed,
            first_name=g["first_name"],
            last_name=g["last_name"],
            role=UserRole.GUEST,
            is_active=True,
        )
        for g in DEMO_GUESTS
    ]

    db.add_all(guests)
    await db.commit()

    logger.info("Seeded %d demo guest accounts.", len(guests))
