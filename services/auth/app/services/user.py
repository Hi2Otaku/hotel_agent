"""User service layer for CRUD operations and admin seeding."""

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User, UserRole


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Fetch a user by email address.

    Args:
        db: The async database session.
        email: The email to look up.

    Returns:
        The User if found, otherwise None.
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    role: UserRole = UserRole.GUEST,
) -> User:
    """Create a new user with a hashed password.

    Args:
        db: The async database session.
        email: The user's email address.
        password: The plaintext password (will be hashed).
        first_name: The user's first name.
        last_name: The user's last name.
        role: The user's role, defaults to GUEST.

    Returns:
        The newly created User.
    """
    user = User(
        email=email,
        password_hash=hash_password(password),
        first_name=first_name,
        last_name=last_name,
        role=role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_or_create_admin(
    db: AsyncSession, email: str, password: str
) -> User:
    """Get existing admin or create one if not found.

    Used for seeding the first admin account on startup.

    Args:
        db: The async database session.
        email: The admin email address.
        password: The admin plaintext password.

    Returns:
        The existing or newly created admin User.
    """
    existing = await get_user_by_email(db, email)
    if existing:
        return existing
    return await create_user(db, email, password, "Admin", "User", UserRole.ADMIN)


async def get_all_users(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> tuple[list[User], int]:
    """Fetch a paginated list of users with total count.

    Args:
        db: The async database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        A tuple of (users list, total count).
    """
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = list(result.scalars().all())
    count_result = await db.execute(select(func.count()).select_from(User))
    total = count_result.scalar()
    return users, total


async def search_users(
    db: AsyncSession, query: str, skip: int = 0, limit: int = 20
) -> tuple[list[User], int]:
    """Search users by first name, last name, or email using ILIKE.

    Args:
        db: The async database session.
        query: The search term to match against names and email.
        skip: Pagination offset.
        limit: Maximum number of records to return.

    Returns:
        A tuple of (matching users list, total count).
    """
    search_term = f"%{query}%"
    filters = or_(
        User.first_name.ilike(search_term),
        User.last_name.ilike(search_term),
        User.email.ilike(search_term),
    )
    count_result = await db.execute(select(func.count()).select_from(User).where(filters))
    total = count_result.scalar()
    result = await db.execute(select(User).where(filters).offset(skip).limit(limit))
    users = list(result.scalars().all())
    return users, total
