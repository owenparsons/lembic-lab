"""Pydantic models for environment management."""

from __future__ import annotations

from pydantic import BaseModel


class EnvironmentConfig(BaseModel):
    venv_path: str = ".venv"
    external: bool = False


class EnvironmentStatus(BaseModel):
    exists: bool
    path: str | None
    external: bool
    python_version: str | None
    package_count: int = 0


class PackageInfo(BaseModel):
    name: str
    version: str


class InstallRequest(BaseModel):
    packages: list[str]


class InstallResult(BaseModel):
    success: bool
    installed: list[str]
    output: str
    requires_restart: bool = True
