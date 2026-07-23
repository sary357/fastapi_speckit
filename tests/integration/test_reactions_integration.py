"""Integration tests for reactions endpoint with database."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from datetime import datetime, timezone

from src.main import app
from src.db.base import Base
from src.models.reaction import ReactionRecord
from src.db.session import get_db

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db:5432/feedback_test"


@pytest.fixture
async def test_db():
    """Create test database and return session."""
    # Create engine
    engine = create_async_engine(TEST_DATABASE_URL)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session factory
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # Yield session
    async with SessionLocal() as session:
        yield session
    
    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
def override_get_db(test_db):
    """Override get_db dependency with test database."""
    async def _get_db():
        yield test_db
    
    return _get_db


@pytest.mark.asyncio
async def test_reaction_saved_to_database(test_db, override_get_db):
    """T015: Verify reaction data is saved to database with correct fields."""
    # Override dependency
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Send like reaction
            response = await client.post(
                "/api/reactions",
                json={"reaction_type": "like"},
            )
            assert response.status_code == 200
            
            # Verify record exists in database
            result = await test_db.execute(
                "SELECT * FROM reaction_record WHERE reaction_type = 'like'"
            )
            record = result.fetchone()
            assert record is not None
            assert record.reaction_type == "like"
            assert record.source_ip is not None
            assert record.received_at is not None
    finally:
        # Clean up dependency override
        app.dependency_overrides.clear()
