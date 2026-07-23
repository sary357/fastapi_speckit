"""Error response utilities."""

from typing import Any, List, Dict
from fastapi import Request, status
from fastapi.responses import JSONResponse


class ErrorResponse:
    """Standardized error response format (aligns with FastAPI 422 and HTTP 429)."""

    @staticmethod
    def unprocessable_entity(detail: Any) -> JSONResponse:
        """Return 422 Unprocessable Entity response."""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": detail if isinstance(detail, list) else [detail]},
        )

    @staticmethod
    def rate_limit_exceeded(detail: str = "Rate limit exceeded") -> JSONResponse:
        """Return 429 Too Many Requests response."""
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": [{"msg": detail, "type": "value_error"}]},
        )
