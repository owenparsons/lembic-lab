"""Checkpoint API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from lembic.server.dependencies import get_state
from lembic.server.state import AppState

router = APIRouter(prefix="/api/checkpoints", tags=["checkpoints"])


class RevertRequest(BaseModel):
    hash: str


class CheckpointResponse(BaseModel):
    hash: str
    timestamp: str
    message: str


@router.get("", response_model=list[CheckpointResponse])
async def list_checkpoints(state: AppState = Depends(get_state)) -> list[CheckpointResponse]:
    if state.checkpoint_manager is None:
        return []
    checkpoints = state.checkpoint_manager.list_checkpoints()
    return [
        CheckpointResponse(hash=cp.hash, timestamp=cp.timestamp, message=cp.message)
        for cp in checkpoints
    ]


@router.post("/revert")
async def revert_to_checkpoint(
    request: RevertRequest,
    state: AppState = Depends(get_state),
) -> dict[str, str]:
    if state.checkpoint_manager is None:
        raise HTTPException(status_code=400, detail="Checkpoints not available (not a git repo)")
    success = state.checkpoint_manager.revert_to_checkpoint(request.hash)
    if not success:
        raise HTTPException(status_code=400, detail="Revert failed")
    # Invalidate manifest cache after revert
    if state.file_manager:
        state.file_manager.invalidate_manifest()
    return {"status": "ok"}
