"""Execution-related models."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ExecutionStatus(str, Enum):
    OK = "ok"
    ERROR = "error"


class CellRunRequest(BaseModel):
    """Request to run a cell or range of cells."""

    cell_ids: list[str] = Field(default_factory=list)


class ExecutionEvent(BaseModel):
    """A single execution event in the log."""

    cell_id: str
    timestamp: datetime
    status: ExecutionStatus
    duration_ms: float
    variables_defined: list[str] = Field(default_factory=list)
    variables_read: list[str] = Field(default_factory=list)
    error: str | None = None


class ExecutionResult(BaseModel):
    """Result of a cell execution returned via REST."""

    cell_id: str
    status: ExecutionStatus
    duration_ms: float
    outputs: list[dict[str, Any]] = Field(default_factory=list)
    error: str | None = None
