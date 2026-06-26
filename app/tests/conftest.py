import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.main import app
from app.models.base import Base
from app.models.user import User, UserRole
from app.core.db import get_db
from app.core.auth import hash_password, create_access_token

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with test_session_maker() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Create tables before each test, drop after."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    """Async HTTP client."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def db():
    """Raw async DB session."""
    async with test_session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def admin_client(client: AsyncClient, db: AsyncSession):
    """AsyncClient pre-authenticated as an admin user."""
    user = User(
        email="admin@test.com",
        password_hash=hash_password("password"),
        first_name="Admin",
        last_name="User",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token({"sub": str(user.id)})
    client.headers["Authorization"] = f"Bearer {token}"
    return client
