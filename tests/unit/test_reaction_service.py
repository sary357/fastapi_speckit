"""Unit tests for ReactionService."""

import pytest
from src.services.reaction_service import ReactionService


def test_invalid_reaction_type_raises_error():
    """T016: ReactionService should reject invalid reaction types."""
    service = ReactionService()
    
    with pytest.raises(ValueError) as exc_info:
        service.validate_reaction_type("invalid")
    
    assert "reaction_type" in str(exc_info.value).lower()


def test_valid_reaction_types():
    """Valid reaction types should not raise error."""
    service = ReactionService()
    
    # These should not raise
    service.validate_reaction_type("like")
    service.validate_reaction_type("dislike")


def test_like_type_accepted():
    """'like' should be accepted as valid reaction type."""
    service = ReactionService()
    assert service.validate_reaction_type("like") is None


def test_dislike_type_accepted():
    """'dislike' should be accepted as valid reaction type."""
    service = ReactionService()
    assert service.validate_reaction_type("dislike") is None
