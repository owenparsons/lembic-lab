"""Execution log: JSONL append-only log of cell executions."""

from __future__ import annotations

import json
import threading
from datetime import datetime
from pathlib import Path

from dataflow.models.cells import CellState
from dataflow.models.execution import ExecutionEvent, ExecutionStatus


class ExecutionLog:
    """Thread-safe JSONL execution log with cell state computation."""

    def __init__(self, log_path: Path) -> None:
        self.log_path = log_path
        self._lock = threading.Lock()

    def append(self, event: ExecutionEvent) -> None:
        """Append an execution event to the log."""
        with self._lock:
            with open(self.log_path, "a") as f:
                f.write(event.model_dump_json() + "\n")

    def read_all(self) -> list[ExecutionEvent]:
        """Read all events from the log."""
        if not self.log_path.exists():
            return []

        events = []
        with open(self.log_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(ExecutionEvent.model_validate_json(line))
        return events

    def read_for_cell(self, cell_id: str) -> list[ExecutionEvent]:
        """Read events for a specific cell."""
        return [e for e in self.read_all() if e.cell_id == cell_id]

    def last_event_for_cell(self, cell_id: str) -> ExecutionEvent | None:
        """Get the most recent execution event for a cell."""
        events = self.read_for_cell(cell_id)
        return events[-1] if events else None

    def compute_cell_state(
        self,
        cell_id: str,
        current_hash: str | None = None,
        last_run_hash: str | None = None,
    ) -> CellState:
        """Compute the current state of a cell based on execution history.

        If current_hash != last_run_hash, the cell has been modified since last run → STALE.
        """
        last = self.last_event_for_cell(cell_id)

        if last is None:
            return CellState.IDLE

        if last.status == ExecutionStatus.ERROR:
            return CellState.ERROR

        # Check if cell content changed since last run
        if current_hash is not None and last_run_hash is not None:
            if current_hash != last_run_hash:
                return CellState.STALE

        return CellState.SUCCESS

    def compute_all_states(self, cell_ids: list[str]) -> dict[str, CellState]:
        """Compute states for all cells."""
        return {cid: self.compute_cell_state(cid) for cid in cell_ids}

    def clear(self) -> None:
        """Clear the execution log."""
        with self._lock:
            if self.log_path.exists():
                self.log_path.unlink()
