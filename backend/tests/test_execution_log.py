"""Tests for the execution log service."""

from datetime import datetime, timezone
from pathlib import Path

import pytest

from dataflow.models.cells import CellState
from dataflow.models.execution import ExecutionEvent, ExecutionStatus
from dataflow.services.execution_log import ExecutionLog


@pytest.fixture
def log(tmp_path: Path) -> ExecutionLog:
    return ExecutionLog(tmp_path / "execution_log.jsonl")


def _make_event(cell_id: str = "abc", status: ExecutionStatus = ExecutionStatus.OK) -> ExecutionEvent:
    return ExecutionEvent(
        cell_id=cell_id,
        timestamp=datetime.now(timezone.utc),
        status=status,
        duration_ms=100.0,
    )


def test_append_and_read(log: ExecutionLog):
    event = _make_event()
    log.append(event)
    events = log.read_all()
    assert len(events) == 1
    assert events[0].cell_id == "abc"


def test_read_empty(log: ExecutionLog):
    assert log.read_all() == []


def test_read_for_cell(log: ExecutionLog):
    log.append(_make_event("a"))
    log.append(_make_event("b"))
    log.append(_make_event("a"))
    assert len(log.read_for_cell("a")) == 2
    assert len(log.read_for_cell("b")) == 1


def test_last_event_for_cell(log: ExecutionLog):
    log.append(_make_event("a", ExecutionStatus.OK))
    log.append(_make_event("a", ExecutionStatus.ERROR))
    last = log.last_event_for_cell("a")
    assert last is not None
    assert last.status == ExecutionStatus.ERROR


def test_compute_cell_state_idle(log: ExecutionLog):
    assert log.compute_cell_state("unknown") == CellState.IDLE


def test_compute_cell_state_success(log: ExecutionLog):
    log.append(_make_event("a", ExecutionStatus.OK))
    assert log.compute_cell_state("a") == CellState.SUCCESS


def test_compute_cell_state_error(log: ExecutionLog):
    log.append(_make_event("a", ExecutionStatus.ERROR))
    assert log.compute_cell_state("a") == CellState.ERROR


def test_compute_cell_state_stale(log: ExecutionLog):
    log.append(_make_event("a", ExecutionStatus.OK))
    state = log.compute_cell_state("a", current_hash="new", last_run_hash="old")
    assert state == CellState.STALE


def test_clear(log: ExecutionLog):
    log.append(_make_event())
    log.clear()
    assert log.read_all() == []
