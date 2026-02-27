"""Notebook manifest models."""

from pydantic import BaseModel, Field

from .cells import CellEntry, CellResponse


class NotebookSettings(BaseModel):
    """Per-notebook settings stored in notebook.yaml."""

    close_terminal_on_exit: bool = True


class NotebookManifest(BaseModel):
    """The notebook manifest (notebook.yaml)."""

    name: str = ""
    settings: NotebookSettings = Field(default_factory=NotebookSettings)
    cells: list[CellEntry] = Field(default_factory=list)


class NotebookResponse(BaseModel):
    """Full notebook state returned to the frontend."""

    cells: list[CellResponse] = Field(default_factory=list)


class ReorderRequest(BaseModel):
    """Request to reorder cells."""

    cell_ids: list[str]
