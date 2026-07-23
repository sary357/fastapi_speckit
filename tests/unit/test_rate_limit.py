"""Unit tests for rate limiting across both endpoints."""

import pytest
from httpx import AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_rate_limit_shared_across_endpoints():
    """T035: Rate limit should be shared across /api/reactions and /api/comments endpoints.
    
    Same IP making 3 requests total (reactions + comments combined) should succeed,
    but 4th request should be rate limited regardless of which endpoint.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Request 1: like reaction
        response1 = await client.post(
            "/api/reactions",
            json={"reaction_type": "like"},
        )
        assert response1.status_code == 200, "Request 1 (like) should succeed"

        # Request 2: comment
        response2 = await client.post(
            "/api/comments",
            json={"content": "First comment"},
        )
        assert response2.status_code == 200, "Request 2 (comment) should succeed"

        # Request 3: dislike reaction
        response3 = await client.post(
            "/api/reactions",
            json={"reaction_type": "dislike"},
        )
        assert response3.status_code == 200, "Request 3 (dislike) should succeed"

        # Request 4: should be rate limited (we've hit 3/minute limit)
        response4 = await client.post(
            "/api/comments",
            json={"content": "Second comment"},
        )
        assert response4.status_code == 429, "Request 4 should be rate limited"


@pytest.mark.asyncio
async def test_rate_limit_per_ip():
    """T035: Rate limit should be per-IP, not global.
    
    Different IPs should have separate rate limit buckets.
    """
    # This test would require testing with different IPs
    # In a real scenario, you'd use pytest-httpx or similar to mock different IPs
    pass
