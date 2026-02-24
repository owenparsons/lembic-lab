"""Project configuration models."""

from pydantic import BaseModel, Field


class ProjectConfig(BaseModel):
    """Project configuration (mirrors dataflow.yaml top-level settings)."""

    name: str = "untitled"
    python_version: str | None = None
    startup_imports: list[str] = Field(default_factory=list)
    auto_save: bool = True


class ProjectInfo(BaseModel):
    """Project info returned by the health/project endpoint."""

    name: str
    path: str
    python_version: str
    kernel_status: str = "idle"
