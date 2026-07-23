"""Unit tests for CommentService."""

import pytest
from src.services.comment_service import CommentService


def test_empty_comment_raises_error():
    """T028: CommentService should reject empty comments."""
    service = CommentService()
    
    with pytest.raises(ValueError) as exc_info:
        service.validate_content("")
    
    assert "empty" in str(exc_info.value).lower()


def test_whitespace_only_comment_raises_error():
    """T028: CommentService should reject whitespace-only comments."""
    service = CommentService()
    
    with pytest.raises(ValueError) as exc_info:
        service.validate_content("   ")
    
    assert "empty" in str(exc_info.value).lower()


def test_comment_over_1000_chars_raises_error():
    """T028: CommentService should reject comments over 1000 characters."""
    service = CommentService()
    
    with pytest.raises(ValueError) as exc_info:
        service.validate_content("a" * 1001)
    
    assert "1000" in str(exc_info.value).lower()


def test_valid_comment_accepted():
    """Valid comments should not raise error."""
    service = CommentService()
    
    # These should not raise
    service.validate_content("This is a valid comment")
    service.validate_content("a" * 1000)  # Exactly at limit
    service.validate_content("   Text with padding   ")  # Should strip and validate


def test_comment_with_special_chars():
    """Comments with special characters should be accepted."""
    service = CommentService()
    
    # Should not raise
    service.validate_content("こんにちは 你好 مرحبا")
    service.validate_content("Comment with @#$%^&*()")
