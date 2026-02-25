"""Cell models for Lembic notebooks."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CellType(str, Enum):
    CODE = "code"
    MARKDOWN = "markdown"
    DEFINE = "define"


class CellState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    STALE = "stale"
    STALE_UPSTREAM = "stale_upstream"


class CellEntry(BaseModel):
    """A cell entry in the notebook manifest."""

    id: str
    name: str
    cell_type: CellType = Field(alias="type")
    file: str

    model_config = {"populate_by_name": True}


class CellCreate(BaseModel):
    """Request to create a new cell."""

    cell_type: CellType = Field(default=CellType.CODE, alias="type")
    name: str | None = None
    content: str = ""
    after_id: str | None = None

    model_config = {"populate_by_name": True}


class CellUpdate(BaseModel):
    """Request to update a cell."""

    name: str | None = None
    content: str | None = None


class CellResponse(BaseModel):
    """Full cell data returned to the frontend."""

    id: str
    name: str
    cell_type: CellType = Field(serialization_alias="type")
    file: str
    content: str = ""
    state: CellState = CellState.IDLE
    outputs: list[dict[str, Any]] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class CellMoveRequest(BaseModel):
    """Request to move a cell to a new position."""

    after_id: str | None = None
