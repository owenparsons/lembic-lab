"""Tests for version history service."""

import time

import pytest

from dataflow.services.version_history import VersionHistory


@pytest.fixture
def vh(tmp_project):
    return VersionHistory(tmp_project)


def test_save_and_list(vh):
    """Save a snapshot and list it."""
    vh.save_snapshot("cell1", "x = 1")
    versions = vh.list_versions("cell1")
    assert len(versions) == 1
    assert versions[0]["cell_id"] == "cell1"
    assert versions[0]["size"] == 5


def test_save_multiple_versions(vh):
    """Multiple saves create multiple versions, newest first."""
    vh.save_snapshot("cell1", "x = 1")
    time.sleep(0.01)  # ensure different timestamps
    vh.save_snapshot("cell1", "x = 2")
    versions = vh.list_versions("cell1")
    assert len(versions) == 2
    # Newest first
    assert versions[0]["timestamp"] >= versions[1]["timestamp"]


def test_get_version_content(vh):
    """Retrieve content of a specific version."""
    vh.save_snapshot("cell1", "x = 42")
    versions = vh.list_versions("cell1")
    ts = versions[0]["timestamp"]
    content = vh.get_version("cell1", ts)
    assert content == "x = 42"


def test_get_nonexistent_version(vh):
    """Getting a version that doesn't exist returns None."""
    result = vh.get_version("cell1", 9999999999999)
    assert result is None


def test_separate_cell_histories(vh):
    """Different cells have independent histories."""
    vh.save_snapshot("cell1", "a = 1")
    vh.save_snapshot("cell2", "b = 2")
    assert len(vh.list_versions("cell1")) == 1
    assert len(vh.list_versions("cell2")) == 1
