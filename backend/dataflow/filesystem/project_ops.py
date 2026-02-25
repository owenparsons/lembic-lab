"""Project initialization and scaffolding."""

from pathlib import Path

import yaml


def initialize_project(project_dir: Path, name: str | None = None) -> None:
    """Create a new DataFlow project with full directory structure."""
    project_dir.mkdir(parents=True, exist_ok=True)

    if name is None:
        name = project_dir.name

    # Create directories
    (project_dir / "cells").mkdir(exist_ok=True)
    (project_dir / "lib").mkdir(exist_ok=True)
    (project_dir / "outputs" / "plots").mkdir(parents=True, exist_ok=True)
    (project_dir / "outputs" / "tables").mkdir(parents=True, exist_ok=True)
    (project_dir / ".dataflow" / "history").mkdir(parents=True, exist_ok=True)

    # Create manifest
    manifest_path = project_dir / "dataflow.yaml"
    if not manifest_path.exists():
        manifest = {
            "name": name,
            "cells": [],
        }
        manifest_path.write_text(yaml.dump(manifest, default_flow_style=False, sort_keys=False))

    # Create .gitignore for DataFlow artifacts
    gitignore_path = project_dir / ".gitignore"
    if not gitignore_path.exists():
        gitignore_path.write_text(
            "# DataFlow\n"
            ".dataflow/\n"
            "execution_log.jsonl\n"
            "outputs/\n"
            "__pycache__/\n"
            "*.pyc\n"
            ".venv/\n"
        )

    # Create lib/__init__.py
    lib_init = project_dir / "lib" / "__init__.py"
    if not lib_init.exists():
        lib_init.write_text('"""Project function library."""\n')

    # Create CLAUDE.md for CC context
    claude_md = project_dir / "CLAUDE.md"
    if not claude_md.exists():
        claude_md.write_text(
            f"# {name}\n\n"
            "This is a DataFlow notebook project. A browser-based notebook UI is\n"
            "watching this directory for changes.\n\n"
            "## Structure\n"
            "- `dataflow.yaml` — Notebook manifest (cell order + metadata)\n"
            "- `cells/` — One Python/Markdown file per cell\n"
            "- `lib/` — Reusable function library (importable from cells)\n"
            "- `outputs/` — Saved plots and tables\n"
            "- `execution_log.jsonl` — Execution history\n\n"
            "## IMPORTANT: Creating cells requires TWO steps\n"
            "A cell only appears in the notebook if it exists BOTH as a file AND\n"
            "in the manifest. Always do both:\n\n"
            "1. Create the file: `cells/{id}_{name}.py`\n"
            "   - `id` is an 8-character hex string (e.g. `a1b2c3d4`)\n"
            "   - `name` is a short kebab-case label (e.g. `load-data`)\n"
            "2. Add an entry to `dataflow.yaml` under `cells:`:\n"
            "   ```yaml\n"
            "   - id: a1b2c3d4\n"
            "     name: load-data\n"
            "     type: code\n"
            "     file: cells/a1b2c3d4_load-data.py\n"
            "   ```\n\n"
            "If you skip step 2, the file exists but the notebook cannot see it.\n\n"
            "## Editing cells\n"
            "- Edit cell files directly; the notebook watches for changes and\n"
            "  updates the UI automatically.\n"
            "- Cell order in the notebook matches the order in `dataflow.yaml`.\n\n"
            "## Deleting cells\n"
            "- Remove the file from `cells/` AND remove its entry from\n"
            "  `dataflow.yaml`.\n\n"
            "## Running cells\n"
            "- Run `dataflow run-cell <id>` to execute a cell headlessly.\n"
            "- Or click the run button in the notebook UI.\n"
        )
