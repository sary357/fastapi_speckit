"""Service layer for reactions (like/dislike) business logic."""

from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.reaction import ReactionRecord, ReactionType


class ReactionService:
    """Service for handling reaction (like/dislike) operations."""

    VALID_TYPES = {"like", "dislike"}

    def validate_reaction_type(self, reaction_type: str) -> None:
        """Validate reaction type is one of allowed values.
        
        Args:
            reaction_type: The reaction type to validate
            
        Raises:
            ValueError: If reaction_type is not valid
        """
        if reaction_type not in self.VALID_TYPES:
            raise ValueError(
                f"reaction_type must be one of {self.VALID_TYPES}, got {reaction_type}"
            )

    async def create_reaction(
        self,
        db: AsyncSession,
        reaction_type: str,
        source_ip: str,
    ) -> ReactionRecord:
        """Create and store a new reaction record.
        
        Args:
            db: AsyncSession for database operations
            reaction_type: Type of reaction (like or dislike)
            source_ip: Source IP address of the request
            
        Returns:
            The created ReactionRecord
            
        Raises:
            ValueError: If reaction_type is invalid
        """
        # Validate reaction type
        self.validate_reaction_type(reaction_type)
        
        # Create record with UTC timestamp
        record = ReactionRecord(
            reaction_type=ReactionType(reaction_type),
            received_at=datetime.now(timezone.utc),
            source_ip=source_ip,
        )
        
        # Save to database
        db.add(record)
        await db.commit()
        await db.refresh(record)
        
        return record
