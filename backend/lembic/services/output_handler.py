"""Output handler: process kernel outputs, save plots/tables to disk."""

from __future__ import annotations

import base64
import json
import time
import uuid
from pathlib import Path
from typing import Any


class OutputHandler:
    """Processes and persists kernel execution outputs."""

    def __init__(self, project_dir: Path) -> None:
        self.project_dir = project_dir
        self.plots_dir = project_dir / "outputs" / "plots"
        self.tables_dir = project_dir / "outputs" / "tables"
        self.plots_dir.mkdir(parents=True, exist_ok=True)
        self.tables_dir.mkdir(parents=True, exist_ok=True)

    def process_display_data(
        self, cell_id: str, data: dict[str, Any], metadata: dict[str, Any]
    ) -> dict[str, Any]:
        """Process display_data output, saving plots to disk.

        Returns the modified data dict with file paths added.
        """
        result = dict(data)

        # Save PNG plots
        if "image/png" in data:
            filename = f"{cell_id}_{int(time.time())}_{uuid.uuid4().hex[:6]}.png"
            path = self.plots_dir / filename
            png_data = base64.b64decode(data["image/png"])
            path.write_bytes(png_data)
            result["_saved_path"] = f"outputs/plots/{filename}"

        # Save SVG plots
        if "image/svg+xml" in data:
            filename = f"{cell_id}_{int(time.time())}_{uuid.uuid4().hex[:6]}.svg"
            path = self.plots_dir / filename
            path.write_text(data["image/svg+xml"])
            result["_saved_path"] = f"outputs/plots/{filename}"

        return result

    def process_table_data(
        self, cell_id: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Process table/DataFrame output, saving as JSON."""
        if "application/json" in data:
            filename = f"{cell_id}_{int(time.time())}.json"
            path = self.tables_dir / filename
            path.write_text(json.dumps(data["application/json"], indent=2))
            data["_saved_path"] = f"outputs/tables/{filename}"

        return data
