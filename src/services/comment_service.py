"""Service layer for comments business logic."""

from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.comment import CommentRecord


class CommentService:
    """Service for handling comment operations."""

    MIN_LENGTH = 1
    MAX_LENGTH = 1000

    def validate_content(self, content: str) -> None:
        """Validate comment content.
        
        Args:
            content: The comment content to validate
            
        Raises:
            ValueError: If content is invalid
        """
        # Strip whitespace and check if empty
        stripped = content.strip()
        if not stripped:
            raise ValueError("Comment content cannot be empty or whitespace-only")
        
        # Check length
        if len(stripped) < self.MIN_LENGTH:
            raise ValueError(f"Comment must be at least {self.MIN_LENGTH} character")
        
        if len(stripped) > self.MAX_LENGTH:
            raise ValueError(
                f"Comment cannot exceed {self.MAX_LENGTH} characters, got {len(stripped)}"
            )

    async def create_comment(
        self,
        db: AsyncSession,
        content: str,
        source_ip: str,
    ) -> CommentRecord:
        """Create and store a new comment record.
        
        Args:
            db: AsyncSession for database operations
            content: Comment content
            source_ip: Source IP address of the request
            
        Returns:
            The created CommentRecord
            
        Raises:
            ValueError: If content is invalid
        """
        # Validate content
        self.validate_content(content)
        
        # Create record with UTC timestamp
        record = CommentRecord(
            content=content.strip(),
            received_at=datetime.now(timezone.utc),
            source_ip=source_ip,
        )
        
        # Save to database
        db.add(record)
        await db.commit()
        await db.refresh(record)
        
        return record
