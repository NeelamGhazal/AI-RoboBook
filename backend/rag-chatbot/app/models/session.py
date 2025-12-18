"""
Session database model.
Represents a user's conversation thread.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID


class Session:
    """Session entity model."""

    def __init__(
        self,
        session_id: UUID,
        created_at: datetime,
        last_activity: datetime,
        user_id: Optional[str] = None,
        status: str = "active",
        metadata: Optional[dict] = None,
    ):
        self.session_id = session_id
        self.user_id = user_id
        self.status = status
        self.created_at = created_at
        self.last_activity = last_activity
        self.metadata = metadata or {}

    @classmethod
    def from_record(cls, record) -> "Session":
        """Create Session from database record."""
        return cls(
            session_id=record["session_id"],
            user_id=record.get("user_id"),
            status=record["status"],
            created_at=record["created_at"],
            last_activity=record["last_activity"],
            metadata=record.get("metadata", {}),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "session_id": str(self.session_id),
            "user_id": self.user_id,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "metadata": self.metadata,
        }
