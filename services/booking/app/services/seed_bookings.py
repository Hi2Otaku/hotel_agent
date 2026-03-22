"""Historical booking seed data generator for portfolio demo.

Generates 800-1200 realistic bookings spanning 6 months of history
plus 30 days into the future. Runs on startup and is idempotent.
"""

import logging
import random
import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import httpx
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.booking import Booking, BookingStatus, generate_confirmation_number

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------
# Guest data pools
# -----------------------------------------------------------------------
FIRST_NAMES = [
    "James", "Emma", "Liam", "Olivia", "Noah", "Ava", "William", "Sophia",
    "Benjamin", "Isabella", "Lucas", "Mia", "Henry", "Charlotte", "Alexander",
    "Amelia", "Sebastian", "Harper", "Jack", "Evelyn", "Daniel", "Aria",
    "Matthew", "Scarlett", "Owen", "Grace", "Ethan", "Chloe", "Samuel", "Lily",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson",
]

# Room type config: name -> (base_price, weight, max_adults, weekend_multiplier)
ROOM_TYPE_CONFIG = {
    "Garden Room": (Decimal("129.00"), 0.35, 2, Decimal("1.10")),
    "Ocean View": (Decimal("199.00"), 0.35, 2, Decimal("1.15")),
    "Junior Suite": (Decimal("279.00"), 0.20, 3, Decimal("1.20")),
    "Beachfront Villa": (Decimal("499.00"), 0.10, 4, Decimal("1.25")),
}

# Stay duration weights (2-7 nights, weighted toward shorter stays)
STAY_DURATIONS = [2, 2, 2, 3, 3, 3, 3, 4, 4, 5, 5, 6, 7]


def _seasonal_multiplier(d: date) -> Decimal:
    """Return seasonal pricing multiplier for a given date."""
    month = d.month
    if month in (6, 7, 8):
        return Decimal("1.30")  # Summer peak
    if month in (9, 10, 11):
        return Decimal("0.85")  # Off-season
    if month == 12 and d.day >= 20:
        return Decimal("1.50")  # Holiday
    if month == 1 and d.day <= 5:
        return Decimal("1.50")  # Holiday
    return Decimal("1.00")


def _is_weekend(d: date) -> bool:
    """Friday=4, Saturday=5 are weekend days."""
    return d.weekday() in (4, 5)


def _booking_volume_multiplier(d: date) -> float:
    """Seasonal and weekday multiplier for number of bookings created per day."""
    mult = 1.0
    month = d.month
    if month in (6, 7, 8):
        mult *= 1.3
    elif month in (9, 10, 11):
        mult *= 0.85
    if d.weekday() in (4, 5):
        mult *= 1.3
    return mult


def _generate_nightly_breakdown(
    check_in: date,
    num_nights: int,
    base_price: Decimal,
    weekend_mult: Decimal,
) -> list[dict]:
    """Generate nightly breakdown matching NightlyRate schema shape."""
    breakdown = []
    for i in range(num_nights):
        night_date = check_in + timedelta(days=i)
        seasonal = _seasonal_multiplier(night_date)
        wknd = weekend_mult if _is_weekend(night_date) else Decimal("1.00")
        final = (base_price * seasonal * wknd).quantize(Decimal("0.01"))
        breakdown.append({
            "date": night_date.strftime("%Y-%m-%d"),
            "base_amount": str(base_price),
            "seasonal_multiplier": str(seasonal),
            "weekend_multiplier": str(wknd),
            "final_amount": str(final),
        })
    return breakdown


async def _fetch_room_types() -> list[dict] | None:
    """Fetch room types from room service API. Returns None if unavailable."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{settings.ROOM_SERVICE_URL}/api/v1/rooms/types/")
            if resp.status_code == 200:
                data = resp.json()
                # Handle both list and paginated response shapes
                if isinstance(data, list):
                    return data
                return data.get("items", data.get("data", []))
    except httpx.HTTPError:
        pass
    return None


async def _fetch_demo_guest_ids() -> list[dict]:
    """Fetch demo guest info from auth service by querying @demo.hotelbook.com emails.

    Returns list of dicts with id, email, first_name, last_name.
    Falls back to empty list if auth service is unavailable.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{settings.AUTH_SERVICE_URL}/api/v1/users/demo-guests"
            )
            if resp.status_code == 200:
                data = resp.json()
                ids = [u for u in data if u.get("id")]
                if ids:
                    logger.info("Fetched %d demo guest IDs from auth service.", len(ids))
                    return ids
    except httpx.HTTPError as e:
        logger.warning("Could not fetch demo guest IDs: %s", e)
    return []


async def _fetch_rooms() -> list[dict]:
    """Fetch rooms from room service API."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{settings.ROOM_SERVICE_URL}/api/v1/rooms/")
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    return data
                return data.get("items", data.get("data", []))
    except httpx.HTTPError:
        pass
    return []


async def seed_historical_bookings(db: AsyncSession) -> None:
    """Seed 800-1200 historical bookings for demo. Idempotent -- skips if > 50 exist."""
    existing_count = await db.scalar(select(func.count()).select_from(Booking))
    if existing_count and existing_count > 50:
        logger.info("Bookings already seeded (%d exist), skipping.", existing_count)
        return

    logger.info("Seeding historical bookings for demo...")

    # Fetch room types from room service
    room_types = await _fetch_room_types()
    if not room_types:
        logger.warning("Room service unavailable -- cannot seed bookings without room type IDs.")
        return

    rooms = await _fetch_rooms()

    # Build room type lookup: name -> {id, rooms}
    rt_lookup: dict[str, dict] = {}
    for rt in room_types:
        name = rt.get("name", "")
        rt_id = rt.get("id", "")
        if name in ROOM_TYPE_CONFIG and rt_id:
            rt_rooms = [r for r in rooms if r.get("room_type_id") == rt_id]
            rt_lookup[name] = {"id": rt_id, "rooms": rt_rooms}

    if not rt_lookup:
        logger.warning("No matching room types found -- cannot seed bookings.")
        return

    # Fetch demo guest IDs from auth service
    demo_guests_full = await _fetch_demo_guest_ids()
    demo_guest_lookup = {g["id"]: g for g in demo_guests_full} if demo_guests_full else {}
    demo_guest_id_list = list(demo_guest_lookup.keys()) if demo_guest_lookup else []
    if demo_guest_id_list:
        logger.info("Using %d demo guest accounts for booking seed.", len(demo_guest_id_list))
    else:
        logger.info("No demo guests available, using random UUIDs for booking seed.")

    # Build weighted room type list for random selection
    weighted_types: list[str] = []
    for name, (_, weight, _, _) in ROOM_TYPE_CONFIG.items():
        if name in rt_lookup:
            weighted_types.extend([name] * int(weight * 100))

    today = date.today()
    start_date = today - timedelta(days=180)
    end_date = today + timedelta(days=30)

    bookings_batch: list[Booking] = []
    total_created = 0

    current_date = start_date
    while current_date <= end_date:
        # Daily booking volume: 2-6 base, adjusted by seasonal/weekend multiplier
        base_count = random.randint(2, 6)
        mult = _booking_volume_multiplier(current_date)
        daily_count = max(1, int(base_count * mult))

        for _ in range(daily_count):
            # Pick room type
            type_name = random.choice(weighted_types)
            rt_info = rt_lookup[type_name]
            base_price, _, max_adults, weekend_mult = ROOM_TYPE_CONFIG[type_name]

            # Stay duration
            num_nights = random.choice(STAY_DURATIONS)
            check_in = current_date
            check_out = check_in + timedelta(days=num_nights)

            # Guest count
            guest_count = random.choices(
                range(1, max_adults + 1),
                weights=[3 if g == 2 else 1 for g in range(1, max_adults + 1)],
                k=1,
            )[0]

            # Pricing with seasonal and weekend adjustments
            breakdown = _generate_nightly_breakdown(
                check_in, num_nights, base_price, weekend_mult
            )
            price_per_night = base_price  # base rate as reference
            total_price = sum(
                Decimal(n["final_amount"]) for n in breakdown
            )

            # Guest data -- use real demo guest IDs when available
            if demo_guest_id_list:
                selected_id = random.choice(demo_guest_id_list)
                guest_user_id = uuid.UUID(selected_id)
                guest_info = demo_guest_lookup[selected_id]
                first_name = guest_info["first_name"]
                last_name = guest_info["last_name"]
                email = guest_info["email"]
            else:
                guest_user_id = uuid.uuid4()
                first_name = random.choice(FIRST_NAMES)
                last_name = random.choice(LAST_NAMES)
                email = f"{first_name.lower()}.{last_name.lower()}@example.com"
            phone = f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"

            # Status based on timing
            if check_out < today:
                # Past booking
                status_roll = random.random()
                if status_roll < 0.70:
                    booking_status = BookingStatus.CHECKED_OUT
                elif status_roll < 0.85:
                    booking_status = BookingStatus.CANCELLED
                elif status_roll < 0.95:
                    booking_status = BookingStatus.NO_SHOW
                else:
                    booking_status = BookingStatus.CONFIRMED
            else:
                # Current/future booking
                status_roll = random.random()
                if status_roll < 0.80:
                    booking_status = BookingStatus.CONFIRMED
                elif status_roll < 0.95:
                    booking_status = BookingStatus.PENDING
                else:
                    booking_status = BookingStatus.CANCELLED

            # Room assignment for checked-in/checked-out bookings
            room_id = None
            if booking_status in (BookingStatus.CHECKED_IN, BookingStatus.CHECKED_OUT):
                type_rooms = rt_info.get("rooms", [])
                if type_rooms:
                    room_id = uuid.UUID(random.choice(type_rooms)["id"])

            # Created at is a few days before check-in (realistic advance booking)
            advance_days = random.randint(1, 60)
            created_at = datetime(
                check_in.year,
                check_in.month,
                check_in.day,
                random.randint(8, 22),
                random.randint(0, 59),
                tzinfo=timezone.utc,
            ) - timedelta(days=advance_days)

            # Build optional fields
            cancelled_at = None
            expires_at = None
            if booking_status == BookingStatus.CANCELLED:
                cancelled_at = created_at + timedelta(
                    hours=random.randint(1, 48)
                )
            if booking_status == BookingStatus.PENDING:
                expires_at = created_at + timedelta(minutes=15)

            booking = Booking(
                id=uuid.uuid4(),
                confirmation_number=generate_confirmation_number(),
                user_id=guest_user_id,
                room_type_id=uuid.UUID(rt_info["id"]),
                room_id=room_id,
                check_in=check_in,
                check_out=check_out,
                guest_count=guest_count,
                status=booking_status,
                total_price=total_price,
                price_per_night=price_per_night,
                currency="USD",
                nightly_breakdown=breakdown,
                guest_first_name=first_name,
                guest_last_name=last_name,
                guest_email=email,
                guest_phone=phone,
                expires_at=expires_at,
                cancelled_at=cancelled_at,
                created_at=created_at,
            )

            bookings_batch.append(booking)

            # Batch insert every 100 bookings
            if len(bookings_batch) >= 100:
                db.add_all(bookings_batch)
                await db.commit()
                total_created += len(bookings_batch)
                bookings_batch = []

        current_date += timedelta(days=1)

    # Flush remaining
    if bookings_batch:
        db.add_all(bookings_batch)
        await db.commit()
        total_created += len(bookings_batch)

    logger.info("Seeded %d historical bookings spanning %s to %s.", total_created, start_date, end_date)
