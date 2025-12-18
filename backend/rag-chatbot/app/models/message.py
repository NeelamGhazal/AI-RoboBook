"""
Message database model.
Represents individual questions and answers within a session.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID


class Message:
    """Message entity model."""

    def __init__(
        self,
        message_id: UUID,
        session_id: UUID,
        role: str,
        content: str,
        timestamp: datetime,
        token_count: int,
        selected_text: Optional[str] = None,
        citations: Optional[list] = None,
        metadata: Optional[dict] = None,
    ):
        self.message_id = message_id
        self.session_id = session_id
        self.role = role
        self.content = content
        self.timestamp = timestamp
        self.token_count = token_count
        self.selected_text = selected_text
        self.citations = citations or []
        self.metadata = metadata or {}

    @classmethod
    def from_record(cls, record) -> "Message":
        """Create Message from database record."""
        return cls(
            message_id=record["message_id"],
            session_id=record["session_id"],
            role=record["role"],
            content=record["content"],
            timestamp=record["timestamp"],
            token_count=record["token_count"],
            selected_text=record.get("selected_text"),
            citations=record.get("citations", []),
            metadata=record.get("metadata", {}),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "message_id": str(self.message_id),
            "session_id": str(self.session_id),
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "token_count": self.token_count,
            "selected_text": self.selected_text,
            "citations": self.citations,
            "metadata": self.metadata,
        }
