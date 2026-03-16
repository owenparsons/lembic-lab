"""Notebook manifest models."""

from pydantic import BaseModel, Field

from .cells import CellEntry, CellResponse


class NotebookSettings(BaseModel):
    """Per-notebook settings stored in notebook.yaml."""

    close_terminal_on_exit: bool = True
    shell: str = "/bin/zsh"


class NotebookSection(BaseModel):
    """A collapsible section in the notebook."""

    id: str
    name: str
    starts_at: str  # cell_id where section begins
    ends_at: str | None = None  # cell_id where section ends (inclusive), None = open-ended
    collapsed: bool = False


class NotebookManifest(BaseModel):
    """The notebook manifest (notebook.yaml)."""

    name: str = ""
    settings: NotebookSettings = Field(default_factory=NotebookSettings)
    cells: list[CellEntry] = Field(default_factory=list)
    sections: list[NotebookSection] = Field(default_factory=list)


class NotebookResponse(BaseModel):
    """Full notebook state returned to the frontend."""

    cells: list[CellResponse] = Field(default_factory=list)
    sections: list[NotebookSection] = Field(default_factory=list)


class ReorderRequest(BaseModel):
    """Request to reorder cells."""

    cell_ids: list[str]
