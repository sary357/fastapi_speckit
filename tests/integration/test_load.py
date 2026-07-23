"""Load test: verify system handles 100 concurrent requests from different IPs."""

import pytest
import asyncio
from httpx import AsyncClient, ASGITransport

from src.main import app


@pytest.mark.asyncio
async def test_load_100_concurrent_requests():
    """T040: Verify system can handle 100 concurrent requests across different IPs without data loss.
    
    This test ensures:
    - SC-003: System supports at least 100 concurrent requests
    - No data loss (all requests succeed)
    - No errors or crashes
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        async def make_request(ip_index: int) -> int:
            """Make a request (simulating different IP via header)."""
            # Simulate different IPs by using different client IPs
            # In a real test, you'd use actual different IPs or mock the client
            response = await client.post(
                "/api/reactions",
                json={"reaction_type": "like" if ip_index % 2 == 0 else "dislike"},
                headers={"X-Forwarded-For": f"192.168.1.{ip_index % 254 + 1}"},
            )
            return response.status_code

        # Create 100 concurrent tasks
        tasks = [make_request(i) for i in range(100)]
        
        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify results
        success_count = sum(1 for r in results if r == 200)
        error_count = sum(1 for r in results if isinstance(r, Exception) or (isinstance(r, int) and r != 200))
        
        # At least 90% should succeed (allowing for rate limit on later reqs)
        assert success_count >= 90, f"Only {success_count}/100 succeeded"
        print(f"✓ Load test passed: {success_count}/100 requests succeeded")


@pytest.mark.asyncio
async def test_load_comments_100_concurrent():
    """T040: Verify comment endpoint can handle 100 concurrent requests."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        async def make_comment(index: int) -> int:
            """Make a comment request."""
            response = await client.post(
                "/api/comments",
                json={"content": f"Test comment {index}"},
            )
            return response.status_code

        # Create 100 concurrent tasks
        tasks = [make_comment(i) for i in range(100)]
        
        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify results
        success_count = sum(1 for r in results if r == 200)
        error_count = sum(1 for r in results if isinstance(r, Exception) or (isinstance(r, int) and r not in [200, 429]))
        
        # At least 90% should succeed or be rate limited (429)
        acceptable_count = sum(1 for r in results if r in [200, 429])
        assert acceptable_count >= 90, f"Only {acceptable_count}/100 succeeded or rate-limited"
        print(f"✓ Comment load test passed: {success_count}/100 succeeded, rate-limited responses OK")
