"""Project and health endpoints."""

import sys

from fastapi import APIRouter, Depends

from dataflow.models.project import ProjectInfo
from dataflow.server.dependencies import get_state
from dataflow.server.state import AppState

router = APIRouter(prefix="/api", tags=["project"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/project", response_model=ProjectInfo)
async def get_project(state: AppState = Depends(get_state)) -> ProjectInfo:
    return ProjectInfo(
        name=state.project_dir.name,
        path=str(state.project_dir),
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        kernel_status="idle" if state.kernel_manager is None else "connected",
    )
