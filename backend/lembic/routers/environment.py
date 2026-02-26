"""Environment management endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from lembic.models.environment import (
    EnvironmentStatus,
    InstallRequest,
    InstallResult,
    PackageInfo,
)
from lembic.server.dependencies import get_env_manager
from lembic.services.env_manager import EnvironmentManager

router = APIRouter(prefix="/api/env", tags=["environment"])


class UninstallRequest(BaseModel):
    packages: list[str]


class SetExternalRequest(BaseModel):
    path: str


class MessageResponse(BaseModel):
    success: bool
    message: str


@router.get("/status", response_model=EnvironmentStatus)
async def env_status(
    env: EnvironmentManager = Depends(get_env_manager),
) -> EnvironmentStatus:
    return await env.get_status()


@router.post("/install", response_model=InstallResult)
async def install_packages(
    req: InstallRequest,
    env: EnvironmentManager = Depends(get_env_manager),
) -> InstallResult:
    return await env.install(req.packages)


@router.post("/uninstall", response_model=MessageResponse)
async def uninstall_packages(
    req: UninstallRequest,
    env: EnvironmentManager = Depends(get_env_manager),
) -> MessageResponse:
    try:
        output = await env.uninstall(req.packages)
        return MessageResponse(success=True, message=output)
    except Exception as e:
        return MessageResponse(success=False, message=str(e))


@router.get("/packages", response_model=list[PackageInfo])
async def list_packages(
    env: EnvironmentManager = Depends(get_env_manager),
) -> list[PackageInfo]:
    return await env.list_packages()


@router.post("/set-external", response_model=MessageResponse)
async def set_external_env(
    req: SetExternalRequest,
    env: EnvironmentManager = Depends(get_env_manager),
) -> MessageResponse:
    try:
        await env.set_external(req.path)
        return MessageResponse(success=True, message=f"Using external env: {req.path}")
    except Exception as e:
        return MessageResponse(success=False, message=str(e))


@router.post("/remove", response_model=MessageResponse)
async def remove_env(
    env: EnvironmentManager = Depends(get_env_manager),
) -> MessageResponse:
    try:
        await env.remove()
        return MessageResponse(success=True, message="Environment removed")
    except Exception as e:
        return MessageResponse(success=False, message=str(e))
