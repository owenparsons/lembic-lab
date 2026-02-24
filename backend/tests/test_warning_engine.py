"""Tests for the warning engine."""

from datetime import datetime, timezone

import pytest

from dataflow.models.cells import CellEntry, CellState, CellType
from dataflow.models.execution import ExecutionEvent, ExecutionStatus
from dataflow.models.notebook import NotebookManifest
from dataflow.services.file_manager import FileManager
from dataflow.services.warning_engine import compute_warnings


@pytest.fixture
def fm(tmp_project):
    return FileManager(tmp_project)


def _event(cell_id: str, status="ok", ts_offset=0, vars_defined=None, vars_read=None):
    return ExecutionEvent(
        cell_id=cell_id,
        timestamp=datetime(2024, 1, 1, 12, 0, ts_offset, tzinfo=timezone.utc),
        status=ExecutionStatus(status),
        duration_ms=100,
        variables_defined=vars_defined or [],
        variables_read=vars_read or [],
    )


def test_all_idle_when_no_events(fm):
    """Cells with no execution events should be idle."""
    c1 = fm.create_cell(content="x = 1")
    c2 = fm.create_cell(content="y = x + 1")
    manifest = fm.load_manifest()

    states, warnings = compute_warnings(manifest, [], fm)

    assert states[c1.id] == CellState.IDLE
    assert states[c2.id] == CellState.IDLE
    assert warnings == []


def test_success_after_execution(fm):
    """Cells should be success after successful execution."""
    c1 = fm.create_cell(content="x = 1")
    manifest = fm.load_manifest()

    events = [_event(c1.id, vars_defined=["x"])]
    states, warnings = compute_warnings(manifest, events, fm)

    assert states[c1.id] == CellState.SUCCESS


def test_error_state(fm):
    """Cells with error in last event should be error."""
    c1 = fm.create_cell(content="x = 1")
    manifest = fm.load_manifest()

    events = [_event(c1.id, status="error")]
    states, warnings = compute_warnings(manifest, events, fm)

    assert states[c1.id] == CellState.ERROR


def test_stale_upstream(fm):
    """Cell depending on a variable redefined after it ran should be stale_upstream."""
    c1 = fm.create_cell(content="x = 1")
    c2 = fm.create_cell(content="y = x + 1")
    manifest = fm.load_manifest()

    # c2 ran first, then c1 ran (redefining x)
    events = [
        _event(c2.id, ts_offset=0, vars_read=["x"], vars_defined=["y"]),
        _event(c1.id, ts_offset=10, vars_defined=["x"]),
    ]

    states, warnings = compute_warnings(manifest, events, fm)

    assert states[c1.id] == CellState.SUCCESS
    assert states[c2.id] == CellState.STALE_UPSTREAM
    assert len(warnings) > 0
    assert "x" in warnings[0]


def test_no_warnings_when_in_order(fm):
    """No stale_upstream warnings when cells run in correct order."""
    c1 = fm.create_cell(content="x = 1")
    c2 = fm.create_cell(content="y = x + 1")
    manifest = fm.load_manifest()

    events = [
        _event(c1.id, ts_offset=0, vars_defined=["x"]),
        _event(c2.id, ts_offset=10, vars_read=["x"], vars_defined=["y"]),
    ]

    states, warnings = compute_warnings(manifest, events, fm)

    assert states[c1.id] == CellState.SUCCESS
    assert states[c2.id] == CellState.SUCCESS
    # Should have no stale upstream warnings
    stale_warnings = [w for w in warnings if "redefined" in w]
    assert len(stale_warnings) == 0
