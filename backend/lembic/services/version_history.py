"""Per-cell version history: snapshot previous versions on save."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


class VersionHistory:
    """Manages per-cell version snapshots in .notebook/history/."""

    def __init__(self, project_dir: Path) -> None:
        self.history_dir = project_dir / ".notebook" / "history"
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def _cell_dir(self, cell_id: str) -> Path:
        d = self.history_dir / cell_id
        d.mkdir(exist_ok=True)
        return d

    def save_snapshot(self, cell_id: str, content: str) -> str:
        """Save a snapshot of cell content. Returns the snapshot filename."""
        cell_dir = self._cell_dir(cell_id)
        timestamp = int(time.time() * 1000)
        filename = f"{timestamp}.py"
        (cell_dir / filename).write_text(content)

        # Also write metadata
        meta_path = cell_dir / f"{timestamp}.meta.json"
        meta_path.write_text(json.dumps({
            "cell_id": cell_id,
            "timestamp": timestamp,
            "size": len(content),
        }))

        # Prune old snapshots (keep last 50)
        self._prune(cell_dir, max_keep=50)
        return filename

    def list_versions(self, cell_id: str) -> list[dict[str, Any]]:
        """List all saved versions for a cell, newest first."""
        cell_dir = self._cell_dir(cell_id)
        versions = []

        for meta_file in sorted(cell_dir.glob("*.meta.json"), reverse=True):
            try:
                meta = json.loads(meta_file.read_text())
                versions.append(meta)
            except (json.JSONDecodeError, OSError):
                continue

        return versions

    def get_version(self, cell_id: str, timestamp: int) -> str | None:
        """Retrieve the content of a specific version."""
        cell_dir = self._cell_dir(cell_id)
        path = cell_dir / f"{timestamp}.py"
        if path.exists():
            return path.read_text()
        return None

    def _prune(self, cell_dir: Path, max_keep: int = 50) -> None:
        """Remove oldest snapshots beyond max_keep."""
        py_files = sorted(cell_dir.glob("*.py"), reverse=True)
        # Exclude meta files
        py_files = [f for f in py_files if not f.name.endswith(".meta.json")]

        for old_file in py_files[max_keep:]:
            old_file.unlink(missing_ok=True)
            meta = old_file.with_suffix(".meta.json")
            if meta.exists():
                meta.unlink(missing_ok=True)
