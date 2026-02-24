"""Tests for Pydantic models serialization/deserialization."""

from dataflow.models.cells import CellCreate, CellEntry, CellResponse, CellState, CellType
from dataflow.models.execution import ExecutionEvent, ExecutionResult, ExecutionStatus
from dataflow.models.notebook import NotebookManifest, NotebookResponse
from dataflow.models.ws_messages import (
    CellStatusMessage,
    DisplayDataMessage,
    ErrorMessage,
    StreamMessage,
)


def test_cell_entry_alias():
    entry = CellEntry(id="abc", name="test", type=CellType.CODE, file="cells/abc_test.py")
    data = entry.model_dump(by_alias=True)
    assert data["type"] == "code"
    assert data["id"] == "abc"


def test_cell_entry_from_dict():
    data = {"id": "abc", "name": "test", "type": "code", "file": "cells/abc_test.py"}
    entry = CellEntry(**data)
    assert entry.cell_type == CellType.CODE


def test_cell_create_defaults():
    create = CellCreate()
    assert create.cell_type == CellType.CODE
    assert create.content == ""
    assert create.name is None


def test_cell_response_serialization():
    resp = CellResponse(
        id="abc",
        name="test",
        cell_type=CellType.CODE,
        file="cells/abc_test.py",
        content="x = 1",
        state=CellState.SUCCESS,
    )
    data = resp.model_dump(by_alias=True)
    assert data["type"] == "code"
    assert data["state"] == "success"


def test_notebook_manifest_empty():
    m = NotebookManifest()
    assert m.cells == []


def test_notebook_manifest_with_cells():
    m = NotebookManifest(
        cells=[
            CellEntry(id="a", name="first", type=CellType.CODE, file="cells/a_first.py"),
            CellEntry(id="b", name="second", type=CellType.MARKDOWN, file="cells/b_second.md"),
        ]
    )
    assert len(m.cells) == 2
    assert m.cells[1].cell_type == CellType.MARKDOWN


def test_execution_event_roundtrip():
    from datetime import datetime, timezone

    event = ExecutionEvent(
        cell_id="abc",
        timestamp=datetime.now(timezone.utc),
        status=ExecutionStatus.OK,
        duration_ms=123.4,
        variables_defined=["x", "y"],
    )
    json_str = event.model_dump_json()
    restored = ExecutionEvent.model_validate_json(json_str)
    assert restored.cell_id == "abc"
    assert restored.status == ExecutionStatus.OK


def test_ws_message_types():
    msg = CellStatusMessage(cell_id="abc", state="running")
    assert msg.type == "cell_status"

    msg = StreamMessage(cell_id="abc", stream="stdout", text="hello")
    assert msg.type == "stream"

    msg = DisplayDataMessage(cell_id="abc", data={"image/png": "base64..."})
    assert msg.type == "display_data"

    msg = ErrorMessage(cell_id="abc", ename="ValueError", evalue="bad", traceback=["line 1"])
    assert msg.type == "error"
