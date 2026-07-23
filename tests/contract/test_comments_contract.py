"""Contract tests for comments endpoint."""

import pytest
from httpx import AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_post_valid_comment_returns_200_ok():
    """T023: POST /api/comments with valid content should return 200 and OK status."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/comments",
            json={"content": "This is a valid comment"},
        )
        assert response.status_code == 200
        assert response.json() == {"status": "OK"}


@pytest.mark.asyncio
async def test_post_comment_empty_content_returns_422():
    """T024: POST /api/comments with empty content should return 422."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/comments",
            json={"content": ""},
        )
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_post_comment_whitespace_only_returns_422():
    """T024: POST /api/comments with whitespace-only content should return 422."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/comments",
            json={"content": "   "},
        )
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_post_comment_over_1000_chars_returns_422():
    """T025: POST /api/comments with content > 1000 chars should return 422."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        over_limit = "a" * 1001
        response = await client.post(
            "/api/comments",
            json={"content": over_limit},
        )
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_post_comment_exactly_1000_chars_returns_200():
    """T025: POST /api/comments with exactly 1000 chars should return 200."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        at_limit = "a" * 1000
        response = await client.post(
            "/api/comments",
            json={"content": at_limit},
        )
        assert response.status_code == 200
        assert response.json() == {"status": "OK"}


@pytest.mark.asyncio
async def test_rate_limit_fourth_comment_returns_429():
    """T026: Fourth comment from same IP within 1 minute should return 429."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Make 3 comment requests (should all succeed)
        for i in range(3):
            response = await client.post(
                "/api/comments",
                json={"content": f"Comment {i+1}"},
            )
            assert response.status_code == 200, f"Request {i+1} failed"

        # Fourth request should be rate limited
        response = await client.post(
            "/api/comments",
            json={"content": "Comment 4"},
        )
        assert response.status_code == 429


@pytest.mark.asyncio
async def test_post_comment_missing_content_returns_422():
    """T024: POST /api/comments without content field should return 422."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/comments",
            json={},
        )
        assert response.status_code == 422
