"""Tests for the file manager service."""

from pathlib import Path

import pytest
import yaml

from dataflow.errors import CellNotFoundError
from dataflow.models.cells import CellType
from dataflow.services.file_manager import FileManager


@pytest.fixture
def fm(tmp_path: Path) -> FileManager:
    """Create a FileManager with a temp project directory."""
    (tmp_path / "cells").mkdir()
    (tmp_path / "dataflow.yaml").write_text(yaml.dump({"cells": []}))
    return FileManager(tmp_path)


def test_load_empty_manifest(fm: FileManager):
    manifest = fm.load_manifest()
    assert manifest.cells == []


def test_create_cell(fm: FileManager):
    entry = fm.create_cell(cell_type=CellType.CODE, content="x = 1")
    assert entry.id
    assert entry.name
    assert entry.file.startswith("cells/")
    assert entry.file.endswith(".py")

    # Verify file exists
    path = fm.project_dir / entry.file
    assert path.exists()
    assert path.read_text() == "x = 1"

    # Verify manifest updated
    fm.invalidate_manifest()
    manifest = fm.load_manifest()
    assert len(manifest.cells) == 1


def test_create_markdown_cell(fm: FileManager):
    entry = fm.create_cell(cell_type=CellType.MARKDOWN, content="# Hello")
    assert entry.file.endswith(".md")


def test_read_cell(fm: FileManager):
    entry = fm.create_cell(content="y = 2")
    content = fm.read_cell(entry.id)
    assert content == "y = 2"


def test_write_cell(fm: FileManager):
    entry = fm.create_cell(content="a = 1")
    fm.write_cell(entry.id, "a = 2")
    assert fm.read_cell(entry.id) == "a = 2"


def test_delete_cell(fm: FileManager):
    entry = fm.create_cell(content="del me")
    cell_path = fm.project_dir / entry.file
    assert cell_path.exists()

    fm.delete_cell(entry.id)
    assert not cell_path.exists()

    fm.invalidate_manifest()
    manifest = fm.load_manifest()
    assert len(manifest.cells) == 0


def test_delete_nonexistent_raises(fm: FileManager):
    with pytest.raises(CellNotFoundError):
        fm.delete_cell("nonexistent")


def test_cell_ordering(fm: FileManager):
    e1 = fm.create_cell(name="first")
    e2 = fm.create_cell(name="second")
    e3 = fm.create_cell(name="third", after_id=e1.id)

    fm.invalidate_manifest()
    manifest = fm.load_manifest()
    names = [c.name for c in manifest.cells]
    assert names == ["first", "third", "second"]


def test_move_cell(fm: FileManager):
    e1 = fm.create_cell(name="a")
    e2 = fm.create_cell(name="b")
    e3 = fm.create_cell(name="c")

    fm.move_cell(e3.id, after_id=e1.id)

    fm.invalidate_manifest()
    manifest = fm.load_manifest()
    names = [c.name for c in manifest.cells]
    assert names == ["a", "c", "b"]


def test_move_to_start(fm: FileManager):
    e1 = fm.create_cell(name="a")
    e2 = fm.create_cell(name="b")

    fm.move_cell(e2.id, after_id=None)

    fm.invalidate_manifest()
    manifest = fm.load_manifest()
    names = [c.name for c in manifest.cells]
    assert names == ["b", "a"]


def test_rename_cell(fm: FileManager):
    entry = fm.create_cell(name="old-name", content="hello")
    fm.rename_cell(entry.id, "new-name")

    fm.invalidate_manifest()
    updated = fm.get_cell_entry(entry.id)
    assert updated.name == "new-name"
    assert fm.read_cell(entry.id) == "hello"


def test_content_hash(fm: FileManager):
    entry = fm.create_cell(content="x = 1")
    h1 = fm.cell_content_hash(entry.id)
    fm.write_cell(entry.id, "x = 2")
    h2 = fm.cell_content_hash(entry.id)
    assert h1 != h2


def test_reorder_cells(fm: FileManager):
    e1 = fm.create_cell(name="a")
    e2 = fm.create_cell(name="b")
    e3 = fm.create_cell(name="c")

    fm.reorder_cells([e3.id, e1.id, e2.id])

    fm.invalidate_manifest()
    manifest = fm.load_manifest()
    names = [c.name for c in manifest.cells]
    assert names == ["c", "a", "b"]
