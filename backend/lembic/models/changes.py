"""Change tracking models."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class ChangeAuthor(str, Enum):
    USER = "user"  # Saved via browser API
    EXTERNAL = "external"  # File watcher detected change (CC or other editor)


class ChangeEvent(BaseModel):
    """A single change event for a cell."""

    cell_id: str
    timestamp: datetime
    author: ChangeAuthor
    content_hash: str
