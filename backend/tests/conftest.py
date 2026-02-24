"""Shared test fixtures for DataFlow backend tests."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """Create a temporary project directory with basic structure."""
    cells_dir = tmp_path / "cells"
    cells_dir.mkdir()
    lib_dir = tmp_path / "lib"
    lib_dir.mkdir()
    outputs_dir = tmp_path / "outputs"
    outputs_dir.mkdir()
    dataflow_dir = tmp_path / ".dataflow"
    dataflow_dir.mkdir()
    (dataflow_dir / "history").mkdir()

    # Create minimal manifest
    manifest = tmp_path / "dataflow.yaml"
    manifest.write_text("cells: []\n")

    return tmp_path
