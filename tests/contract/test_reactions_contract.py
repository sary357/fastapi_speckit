"""Contract tests for reactions (like/dislike) endpoint."""

import pytest
from httpx import AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_post_like_returns_200_ok():
    """T011: POST /api/reactions with like should return 200 and OK status."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/reactions",
            json={"reaction_type": "like"},
        )
        assert response.status_code == 200
        assert response.json() == {"status": "OK"}


@pytest.mark.asyncio
async def test_post_dislike_returns_200_ok():
    """T012: POST /api/reactions with dislike should return 200 and OK status."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/reactions",
            json={"reaction_type": "dislike"},
        )
        assert response.status_code == 200
        assert response.json() == {"status": "OK"}


@pytest.mark.asyncio
async def test_post_reaction_missing_type_returns_422():
    """T013: POST /api/reactions missing reaction_type should return 422."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/reactions",
            json={},
        )
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_post_reaction_invalid_type_returns_422():
    """T013: POST /api/reactions with invalid reaction_type should return 422."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/reactions",
            json={"reaction_type": "invalid"},
        )
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_rate_limit_fourth_request_returns_429():
    """T014: Fourth reaction request from same IP within 1 minute should return 429."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Make 3 requests (should all succeed)
        for i in range(3):
            response = await client.post(
                "/api/reactions",
                json={"reaction_type": "like"},
            )
            assert response.status_code == 200, f"Request {i+1} failed"

        # Fourth request should be rate limited
        response = await client.post(
            "/api/reactions",
            json={"reaction_type": "like"},
        )
        assert response.status_code == 429
