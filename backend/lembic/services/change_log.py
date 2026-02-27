"""Change log: append-only JSONL log of cell changes with author attribution."""

from __future__ import annotations

import threading
from datetime import datetime
from pathlib import Path

from lembic.models.changes import ChangeAuthor, ChangeEvent


class ChangeLog:
    """Thread-safe JSONL change log tracking who changed each cell."""

    def __init__(self, log_path: Path) -> None:
        self.log_path = log_path
        self._lock = threading.Lock()

    def append(self, cell_id: str, author: ChangeAuthor, content_hash: str) -> None:
        """Record a change event."""
        event = ChangeEvent(
            cell_id=cell_id,
            timestamp=datetime.now(),
            author=author,
            content_hash=content_hash,
        )
        with self._lock:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_path, "a") as f:
                f.write(event.model_dump_json() + "\n")

    def read_all(self) -> list[ChangeEvent]:
        """Read all change events."""
        if not self.log_path.exists():
            return []

        events = []
        with open(self.log_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(ChangeEvent.model_validate_json(line))
        return events

    def last_change_for_cell(self, cell_id: str) -> ChangeEvent | None:
        """Get the most recent change event for a cell."""
        last = None
        for event in self.read_all():
            if event.cell_id == cell_id:
                last = event
        return last
