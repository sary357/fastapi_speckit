"""Unit tests for rate limiting across both endpoints."""

import pytest
from fastapi.testclient import TestClient

from src.main import app


def test_rate_limit_shared_across_endpoints():
    """T035: Rate limit should be shared across /api/reactions and /api/comments endpoints.
    
    Same IP making 5 requests total (reactions + comments combined) should succeed,
    but 6th request should be rate limited regardless of which endpoint.
    """
    # Use TestClient which properly sets request.client
    client = TestClient(app)
    
    # Request 1: like reaction
    response1 = client.post(
        "/api/reactions",
        json={"reaction_type": "like"},
    )
    assert response1.status_code == 200, "Request 1 (like) should succeed"

    # Request 2: comment
    response2 = client.post(
        "/api/comments",
        json={"content": "First comment"},
    )
    assert response2.status_code == 200, "Request 2 (comment) should succeed"

    # Request 3: dislike reaction
    response3 = client.post(
        "/api/reactions",
        json={"reaction_type": "dislike"},
    )
    assert response3.status_code == 200, "Request 3 (dislike) should succeed"

    # Request 4: another comment
    response4 = client.post(
        "/api/comments",
        json={"content": "Second comment"},
    )
    assert response4.status_code == 200, "Request 4 (comment) should succeed"

    # Request 5: another like
    response5 = client.post(
        "/api/reactions",
        json={"reaction_type": "like"},
    )
    assert response5.status_code == 200, "Request 5 (like) should succeed"

    # Request 6: should be rate limited (we've hit 5/minute limit)
    response6 = client.post(
        "/api/comments",
        json={"content": "Third comment"},
    )
    assert response6.status_code == 429, "Request 6 should be rate limited"
