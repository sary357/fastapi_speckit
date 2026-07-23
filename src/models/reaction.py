"""SQLAlchemy ORM model for reaction records."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Enum
import enum

from src.db.base import Base


class ReactionType(str, enum.Enum):
    """Enum for reaction types."""

    LIKE = "like"
    DISLIKE = "dislike"


class ReactionRecord(Base):
    """Database model for user reactions (like/dislike)."""

    __tablename__ = "reaction_record"

    id = Column(Integer, primary_key=True, index=True)
    reaction_type = Column(Enum(ReactionType), nullable=False, index=True)
    received_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    source_ip = Column(String(45), nullable=False, index=True)  # IPv4 (15) + IPv6 (39)

    def __repr__(self):
        return f"<ReactionRecord(id={self.id}, type={self.reaction_type}, ip={self.source_ip}, at={self.received_at})>"
