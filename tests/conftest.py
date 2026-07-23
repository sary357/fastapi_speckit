"""Pytest configuration and fixtures for all tests."""

import pytest
import pytest_asyncio
from slowapi.util import get_remote_address
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.base import Base
from src.main import app
from src.db.session import get_db
from src.core.rate_limit import limiter


# SQLite in-memory test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def test_db_engine():
    """Create an async SQLite engine with in-memory database."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def test_db_session(test_db_engine):
    """Create a new database session for each test."""
    async_session = async_sessionmaker(
        test_db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture(autouse=True)
def _override_get_db(test_db_session):
    """Override the get_db dependency for all tests."""

    async def get_test_db():
        """Return the test database session."""
        yield test_db_session

    app.dependency_overrides[get_db] = get_test_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """Reset the rate limiter storage before each test."""
    limiter.reset()
    yield
