"""SQLAlchemy ORM model for comment records."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text

from src.db.base import Base


class CommentRecord(Base):
    """Database model for user comments."""

    __tablename__ = "comment_record"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    received_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    source_ip = Column(String(45), nullable=False, index=True)  # IPv4 (15) + IPv6 (39)

    def __repr__(self):
        return f"<CommentRecord(id={self.id}, len={len(self.content)}, ip={self.source_ip}, at={self.received_at})>"
