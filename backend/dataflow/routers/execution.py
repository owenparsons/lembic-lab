"""Execution endpoints: run cells, kernel control."""

from fastapi import APIRouter, Depends, HTTPException

from dataflow.errors import CellNotFoundError, KernelNotStartedError
from dataflow.models.execution import CellRunRequest, ExecutionResult
from dataflow.server.dependencies import get_cell_executor, get_state
from dataflow.server.state import AppState
from dataflow.services.cell_executor import CellExecutor

router = APIRouter(prefix="/api", tags=["execution"])


@router.post("/run/{cell_id}", response_model=ExecutionResult)
async def run_cell(
    cell_id: str,
    executor: CellExecutor = Depends(get_cell_executor),
) -> ExecutionResult:
    try:
        return await executor.execute_cell(cell_id)
    except CellNotFoundError:
        raise HTTPException(status_code=404, detail=f"Cell not found: {cell_id}")
    except KernelNotStartedError:
        raise HTTPException(status_code=503, detail="Kernel not started")


@router.post("/run/range", response_model=list[ExecutionResult])
async def run_range(
    request: CellRunRequest,
    executor: CellExecutor = Depends(get_cell_executor),
) -> list[ExecutionResult]:
    results = []
    for cell_id in request.cell_ids:
        try:
            result = await executor.execute_cell(cell_id)
            results.append(result)
        except CellNotFoundError:
            raise HTTPException(status_code=404, detail=f"Cell not found: {cell_id}")
    return results


@router.post("/run/all", response_model=list[ExecutionResult])
async def run_all(
    executor: CellExecutor = Depends(get_cell_executor),
) -> list[ExecutionResult]:
    return await executor.execute_all()


@router.post("/kernel/interrupt")
async def interrupt_kernel(state: AppState = Depends(get_state)) -> dict[str, str]:
    if state.kernel_manager is None:
        raise HTTPException(status_code=503, detail="Kernel not started")
    await state.kernel_manager.interrupt()
    return {"status": "ok"}


@router.post("/kernel/restart")
async def restart_kernel(state: AppState = Depends(get_state)) -> dict[str, str]:
    if state.kernel_manager is None:
        raise HTTPException(status_code=503, detail="Kernel not started")
    await state.kernel_manager.restart()
    return {"status": "ok"}
