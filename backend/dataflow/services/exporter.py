"""Export service: convert notebook to .ipynb, .py, or package."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from dataflow.models.export import ExportFormat, ExportResult
from dataflow.services.file_manager import FileManager


class Exporter:
    """Exports notebook to various formats."""

    def __init__(self, file_manager: FileManager) -> None:
        self.fm = file_manager
        self.project_name = file_manager.project_dir.name

    def export(self, format: ExportFormat) -> ExportResult:
        if format == ExportFormat.IPYNB:
            return self._export_ipynb()
        elif format == ExportFormat.PYTHON:
            return self._export_python()
        elif format == ExportFormat.PACKAGE:
            return self._export_package()
        else:
            raise ValueError(f"Unknown format: {format}")

    def _export_ipynb(self) -> ExportResult:
        """Export as Jupyter notebook (.ipynb)."""
        manifest = self.fm.load_manifest()
        cells = []

        for entry in manifest.cells:
            content = self.fm.read_cell(entry.id)
            cell_type = entry.cell_type.value

            if cell_type in ("code", "define"):
                cells.append({
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {
                        "dataflow_id": entry.id,
                        "dataflow_name": entry.name,
                    },
                    "outputs": [],
                    "source": content.splitlines(keepends=True),
                })
            elif cell_type == "markdown":
                cells.append({
                    "cell_type": "markdown",
                    "metadata": {
                        "dataflow_id": entry.id,
                        "dataflow_name": entry.name,
                    },
                    "source": content.splitlines(keepends=True),
                })

        notebook: dict[str, Any] = {
            "nbformat": 4,
            "nbformat_minor": 5,
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3",
                },
                "language_info": {
                    "name": "python",
                    "version": "3.12.0",
                },
            },
            "cells": cells,
        }

        out_path = self.fm.project_dir / "exports" / f"{self.project_name}.ipynb"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(notebook, indent=2))

        return ExportResult(
            format=ExportFormat.IPYNB,
            path=str(out_path.relative_to(self.fm.project_dir)),
            message=f"Exported {len(cells)} cells to {out_path.name}",
        )

    def _export_python(self) -> ExportResult:
        """Export as Python script with # %% cell markers."""
        manifest = self.fm.load_manifest()
        lines: list[str] = []

        for i, entry in enumerate(manifest.cells):
            content = self.fm.read_cell(entry.id)
            cell_type = entry.cell_type.value

            if i > 0:
                lines.append("")

            if cell_type == "markdown":
                lines.append(f"# %% [markdown] {entry.name}")
                for line in content.splitlines():
                    lines.append(f"# {line}" if line.strip() else "#")
            else:
                lines.append(f"# %% {entry.name}")
                lines.append(content)

        out_path = self.fm.project_dir / "exports" / f"{self.project_name}.py"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("\n".join(lines) + "\n")

        return ExportResult(
            format=ExportFormat.PYTHON,
            path=str(out_path.relative_to(self.fm.project_dir)),
            message=f"Exported to {out_path.name}",
        )

    def _export_package(self) -> ExportResult:
        """Export as a Python package with src/ layout."""
        manifest = self.fm.load_manifest()
        pkg_name = self.project_name.replace("-", "_").replace(" ", "_")
        pkg_dir = self.fm.project_dir / "exports" / pkg_name
        src_dir = pkg_dir / "src" / pkg_name
        src_dir.mkdir(parents=True, exist_ok=True)

        # __init__.py
        init_lines = [f'"""Package {pkg_name} — exported from DataFlow."""']

        # Write each code cell as a module
        for entry in manifest.cells:
            content = self.fm.read_cell(entry.id)
            if entry.cell_type.value in ("code", "define"):
                module_name = entry.name.replace("-", "_").replace(" ", "_")
                (src_dir / f"{module_name}.py").write_text(content)
                init_lines.append(f"from .{module_name} import *  # noqa: F403")

        (src_dir / "__init__.py").write_text("\n".join(init_lines) + "\n")

        # pyproject.toml
        pyproject = f"""[project]
name = "{pkg_name}"
version = "0.1.0"
requires-python = ">=3.10"
"""
        (pkg_dir / "pyproject.toml").write_text(pyproject)

        return ExportResult(
            format=ExportFormat.PACKAGE,
            path=str(pkg_dir.relative_to(self.fm.project_dir)),
            message=f"Exported as package to {pkg_dir.name}/",
        )
