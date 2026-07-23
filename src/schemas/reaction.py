"""Pydantic schemas for reaction requests and responses."""

from typing import Literal
from pydantic import BaseModel, Field


class ReactionRequest(BaseModel):
    """Request schema for POST /api/reactions."""

    reaction_type: Literal["like", "dislike"] = Field(
        ...,
        description="Type of reaction: like or dislike",
    )


class StatusResponse(BaseModel):
    """Success response schema for reactions and comments."""

    status: Literal["OK"] = "OK"

    model_config = {"json_schema_extra": {"example": {"status": "OK"}}}


class ErrorDetail(BaseModel):
    """Error detail schema."""

    msg: str
    type: str


class ErrorResponse(BaseModel):
    """Error response schema (422/429)."""

    detail: list[ErrorDetail] | list[str]
