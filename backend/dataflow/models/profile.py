"""Data profiling models."""

from typing import Any

from pydantic import BaseModel, Field


class ColumnProfile(BaseModel):
    """Profile for a single DataFrame column."""

    name: str
    dtype: str
    count: int
    null_count: int
    unique_count: int
    top_values: list[dict[str, Any]] = Field(default_factory=list)
    mean: float | None = None
    std: float | None = None
    min: Any | None = None
    max: Any | None = None
    median: float | None = None


class DataProfile(BaseModel):
    """Full profile of a DataFrame variable."""

    variable_name: str
    shape: tuple[int, int]
    columns: list[ColumnProfile] = Field(default_factory=list)
    memory_usage_bytes: int = 0
    sample_rows: list[dict[str, Any]] = Field(default_factory=list)
