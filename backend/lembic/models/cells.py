"""Cell models for Lembic notebooks."""

from enum import Enum
from typing import Any

from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field

StrCoerce = Annotated[str, BeforeValidator(lambda v: str(v))]


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


class CellAnnotation(BaseModel):
    """A per-cell annotation (note, warning, etc.)."""

    text: str
    style: str = "info"  # info | warning | success | error


class CellEntry(BaseModel):
    """A cell entry in the notebook manifest."""

    id: StrCoerce
    name: str
    cell_type: CellType = Field(alias="type")
    file: str
    annotation: CellAnnotation | None = None

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
    annotation: CellAnnotation | None = None


class CellResponse(BaseModel):
    """Full cell data returned to the frontend."""

    id: str
    name: str
    cell_type: CellType = Field(serialization_alias="type")
    file: str
    content: str = ""
    state: CellState = CellState.IDLE
    outputs: list[dict[str, Any]] = Field(default_factory=list)
    annotation: CellAnnotation | None = None
    last_author: str | None = None  # "user" | "external"
    last_modified: str | None = None  # ISO 8601

    model_config = {"populate_by_name": True}


class CellMoveRequest(BaseModel):
    """Request to move a cell to a new position."""

    after_id: str | None = None
