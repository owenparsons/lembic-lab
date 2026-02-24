"""Variable explorer models."""

from typing import Any

from pydantic import BaseModel


class VariableInfo(BaseModel):
    """Information about a variable in the kernel namespace."""

    name: str
    var_type: str
    shape: str | None = None
    size_bytes: int | None = None
    preview: str = ""
