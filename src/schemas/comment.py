"""Pydantic schemas for comment requests and responses."""

from pydantic import BaseModel, Field, field_validator


class CommentRequest(BaseModel):
    """Request schema for POST /api/comments."""

    content: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Comment content (1-1000 characters after stripping whitespace)",
    )

    @field_validator("content")
    @classmethod
    def validate_content_not_empty(cls, v: str) -> str:
        """Ensure content is not just whitespace."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("content cannot be empty or whitespace-only")
        return stripped


class CommentResponse(BaseModel):
    """Response schema for successful comment submission."""

    status: str = "OK"
