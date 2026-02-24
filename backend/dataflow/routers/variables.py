"""Variable explorer endpoint."""

from fastapi import APIRouter, Depends

from dataflow.models.variables import VariableInfo
from dataflow.server.dependencies import get_state
from dataflow.server.state import AppState

router = APIRouter(prefix="/api", tags=["variables"])


@router.get("/variables", response_model=list[VariableInfo])
async def list_variables(state: AppState = Depends(get_state)) -> list[VariableInfo]:
    if state.kernel_manager is None or not state.kernel_manager.is_started:
        return []
    raw = await state.kernel_manager.get_variables()
    return [VariableInfo(**v) for v in raw]
