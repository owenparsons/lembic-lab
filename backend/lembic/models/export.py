"""Export models."""

from enum import Enum

from pydantic import BaseModel


class ExportFormat(str, Enum):
    IPYNB = "ipynb"
    PYTHON = "python"
    PACKAGE = "package"


class ExportRequest(BaseModel):
    """Request to export the notebook."""

    format: ExportFormat


class ExportResult(BaseModel):
    """Result of an export operation."""

    format: ExportFormat
    path: str
    message: str = ""
