"""Beach resort seed data: 4 room types, 55 rooms, base rates, seasonal rates, weekend surcharges.

Idempotent -- skips if data already exists.
"""

import logging
from datetime import date
from decimal import Decimal

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.room import Room, RoomStatus
from app.models.room_type import RoomType
from app.models.rate import BaseRate, SeasonalRate, WeekendSurcharge

logger = logging.getLogger(__name__)


async def seed_data(db: AsyncSession) -> None:
    """Seed beach resort demo data. Idempotent -- skips if data exists."""
    count = await db.scalar(select(func.count()).select_from(RoomType))
    if count and count > 0:
        logger.info("Seed data already exists, skipping.")
        return

    logger.info("Seeding beach resort demo data...")

    # -----------------------------------------------------------------------
    # Room Types
    # -----------------------------------------------------------------------
    garden_room = RoomType(
        name="Garden Room",
        slug="garden-room",
        description="Cozy room overlooking the tropical garden with modern amenities.",
        max_adults=2,
        max_children=1,
        bed_config=[{"type": "queen", "count": 1}],
        amenities={
            "Comfort": ["AC", "Mini Fridge"],
            "Tech": ["WiFi", "Flat Screen TV"],
            "Bathroom": ["Walk-in Shower"],
        },
        photo_urls=[
            "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800"
        ],
    )
    ocean_view = RoomType(
        name="Ocean View",
        slug="ocean-view",
        description="Spacious room with stunning ocean views from a private balcony.",
        max_adults=2,
        max_children=2,
        bed_config=[{"type": "king", "count": 1}],
        amenities={
            "Comfort": ["AC", "Mini Bar", "Balcony"],
            "Tech": ["WiFi", "Smart TV", "Bluetooth Speaker"],
            "Bathroom": ["Rainfall Shower", "Bathrobe"],
        },
        photo_urls=[
            "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800"
        ],
    )
    junior_suite = RoomType(
        name="Junior Suite",
        slug="junior-suite",
        description="Luxurious suite with separate living area and premium amenities.",
        max_adults=3,
        max_children=2,
        bed_config=[{"type": "king", "count": 1}, {"type": "sofa", "count": 1}],
        amenities={
            "Comfort": ["AC", "Mini Bar", "Balcony", "Living Area"],
            "Tech": ["WiFi", "Smart TV", "Bluetooth Speaker", "USB Charging"],
            "Bathroom": [
                "Rainfall Shower",
                "Soaking Tub",
                "Bathrobe",
                "Slippers",
            ],
        },
        photo_urls=[
            "https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800"
        ],
    )
    beachfront_villa = RoomType(
        name="Beachfront Villa",
        slug="beachfront-villa",
        description="Private beachfront villa with pool, full kitchen, and tropical garden.",
        max_adults=4,
        max_children=3,
        bed_config=[{"type": "king", "count": 1}, {"type": "twin", "count": 2}],
        amenities={
            "Comfort": [
                "AC",
                "Full Kitchen",
                "Private Pool",
                "Sun Deck",
                "Garden",
            ],
            "Tech": [
                "WiFi",
                "Smart TV",
                "Surround Sound",
                "Smart Home Controls",
            ],
            "Bathroom": [
                "Outdoor Shower",
                "Soaking Tub",
                "Double Vanity",
                "Bathrobe",
                "Slippers",
            ],
        },
        photo_urls=[
            "https://images.unsplash.com/photo-1602002418082-a4443e081dd1?w=800"
        ],
    )

    room_types = [garden_room, ocean_view, junior_suite, beachfront_villa]
    db.add_all(room_types)
    await db.commit()

    # Refresh to get IDs
    for rt in room_types:
        await db.refresh(rt)

    # -----------------------------------------------------------------------
    # Rooms (55 total)
    # -----------------------------------------------------------------------
    rooms = []

    # Garden Room: 101-115 (floor 1, 15 rooms)
    for i in range(15):
        rooms.append(
            Room(
                room_number=str(101 + i),
                floor=1,
                room_type_id=garden_room.id,
                status=RoomStatus.AVAILABLE,
            )
        )

    # Ocean View: 201-220 (floor 2, 20 rooms)
    for i in range(20):
        rooms.append(
            Room(
                room_number=str(201 + i),
                floor=2,
                room_type_id=ocean_view.id,
                status=RoomStatus.AVAILABLE,
            )
        )

    # Junior Suite: 301-315 (floor 3, 15 rooms)
    for i in range(15):
        rooms.append(
            Room(
                room_number=str(301 + i),
                floor=3,
                room_type_id=junior_suite.id,
                status=RoomStatus.AVAILABLE,
            )
        )

    # Beachfront Villa: V01-V05 (ground floor, 5 rooms)
    for i in range(5):
        rooms.append(
            Room(
                room_number=f"V{i + 1:02d}",
                floor=0,
                room_type_id=beachfront_villa.id,
                status=RoomStatus.AVAILABLE,
            )
        )

    db.add_all(rooms)
    await db.commit()

    # -----------------------------------------------------------------------
    # Base Rates
    # -----------------------------------------------------------------------
    base_rates = [
        # Garden Room
        BaseRate(
            room_type_id=garden_room.id,
            min_occupancy=1,
            max_occupancy=2,
            amount=Decimal("129.00"),
            currency="USD",
        ),
        BaseRate(
            room_type_id=garden_room.id,
            min_occupancy=3,
            max_occupancy=3,
            amount=Decimal("159.00"),
            currency="USD",
        ),
        # Ocean View
        BaseRate(
            room_type_id=ocean_view.id,
            min_occupancy=1,
            max_occupancy=2,
            amount=Decimal("199.00"),
            currency="USD",
        ),
        BaseRate(
            room_type_id=ocean_view.id,
            min_occupancy=3,
            max_occupancy=4,
            amount=Decimal("249.00"),
            currency="USD",
        ),
        # Junior Suite
        BaseRate(
            room_type_id=junior_suite.id,
            min_occupancy=1,
            max_occupancy=2,
            amount=Decimal("279.00"),
            currency="USD",
        ),
        BaseRate(
            room_type_id=junior_suite.id,
            min_occupancy=3,
            max_occupancy=5,
            amount=Decimal("349.00"),
            currency="USD",
        ),
        # Beachfront Villa
        BaseRate(
            room_type_id=beachfront_villa.id,
            min_occupancy=1,
            max_occupancy=2,
            amount=Decimal("499.00"),
            currency="USD",
        ),
        BaseRate(
            room_type_id=beachfront_villa.id,
            min_occupancy=3,
            max_occupancy=4,
            amount=Decimal("599.00"),
            currency="USD",
        ),
        BaseRate(
            room_type_id=beachfront_villa.id,
            min_occupancy=5,
            max_occupancy=7,
            amount=Decimal("699.00"),
            currency="USD",
        ),
    ]
    db.add_all(base_rates)
    await db.commit()

    # -----------------------------------------------------------------------
    # Seasonal Rates (applied to all room types)
    # -----------------------------------------------------------------------
    seasonal_rates = []
    for rt in room_types:
        seasonal_rates.extend(
            [
                SeasonalRate(
                    room_type_id=rt.id,
                    name="Summer Peak",
                    start_date=date(2026, 6, 1),
                    end_date=date(2026, 8, 31),
                    multiplier=Decimal("1.30"),
                ),
                SeasonalRate(
                    room_type_id=rt.id,
                    name="Holiday Season",
                    start_date=date(2026, 12, 20),
                    end_date=date(2027, 1, 5),
                    multiplier=Decimal("1.50"),
                ),
                SeasonalRate(
                    room_type_id=rt.id,
                    name="Off Season",
                    start_date=date(2026, 9, 1),
                    end_date=date(2026, 11, 30),
                    multiplier=Decimal("0.85"),
                ),
            ]
        )
    db.add_all(seasonal_rates)
    await db.commit()

    # -----------------------------------------------------------------------
    # Weekend Surcharges
    # -----------------------------------------------------------------------
    weekend_surcharges = [
        WeekendSurcharge(
            room_type_id=garden_room.id,
            multiplier=Decimal("1.10"),
            days=[4, 5],
        ),
        WeekendSurcharge(
            room_type_id=ocean_view.id,
            multiplier=Decimal("1.15"),
            days=[4, 5],
        ),
        WeekendSurcharge(
            room_type_id=junior_suite.id,
            multiplier=Decimal("1.20"),
            days=[4, 5],
        ),
        WeekendSurcharge(
            room_type_id=beachfront_villa.id,
            multiplier=Decimal("1.25"),
            days=[4, 5],
        ),
    ]
    db.add_all(weekend_surcharges)
    await db.commit()

    logger.info(
        "Seeded beach resort: %d room types, %d rooms, %d base rates, "
        "%d seasonal rates, %d weekend surcharges",
        len(room_types),
        len(rooms),
        len(base_rates),
        len(seasonal_rates),
        len(weekend_surcharges),
    )
