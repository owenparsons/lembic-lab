"""Cell CRUD endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from dataflow.errors import CellNotFoundError
from dataflow.models.cells import (
    CellCreate,
    CellMoveRequest,
    CellResponse,
    CellState,
    CellUpdate,
)
from dataflow.server.dependencies import get_file_manager
from dataflow.services.file_manager import FileManager

router = APIRouter(prefix="/api/cells", tags=["cells"])


@router.get("", response_model=list[CellResponse])
async def list_cells(fm: FileManager = Depends(get_file_manager)) -> list[CellResponse]:
    manifest = fm.load_manifest()
    cells = []
    for entry in manifest.cells:
        content = fm.read_cell(entry.id)
        cells.append(
            CellResponse(
                id=entry.id,
                name=entry.name,
                cell_type=entry.cell_type,
                file=entry.file,
                content=content,
                state=CellState.IDLE,
            )
        )
    return cells


@router.post("", response_model=CellResponse, status_code=201)
async def create_cell(
    request: CellCreate,
    fm: FileManager = Depends(get_file_manager),
) -> CellResponse:
    entry = fm.create_cell(
        cell_type=request.cell_type,
        name=request.name,
        content=request.content,
        after_id=request.after_id,
    )
    return CellResponse(
        id=entry.id,
        name=entry.name,
        cell_type=entry.cell_type,
        file=entry.file,
        content=request.content,
        state=CellState.IDLE,
    )


@router.get("/{cell_id}", response_model=CellResponse)
async def get_cell(
    cell_id: str,
    fm: FileManager = Depends(get_file_manager),
) -> CellResponse:
    try:
        entry = fm.get_cell_entry(cell_id)
    except CellNotFoundError:
        raise HTTPException(status_code=404, detail=f"Cell not found: {cell_id}")
    content = fm.read_cell(cell_id)
    return CellResponse(
        id=entry.id,
        name=entry.name,
        cell_type=entry.cell_type,
        file=entry.file,
        content=content,
        state=CellState.IDLE,
    )


@router.put("/{cell_id}", response_model=CellResponse)
async def update_cell(
    cell_id: str,
    request: CellUpdate,
    fm: FileManager = Depends(get_file_manager),
) -> CellResponse:
    try:
        entry = fm.get_cell_entry(cell_id)
    except CellNotFoundError:
        raise HTTPException(status_code=404, detail=f"Cell not found: {cell_id}")

    if request.name is not None:
        fm.rename_cell(cell_id, request.name)
        entry = fm.get_cell_entry(cell_id)

    if request.content is not None:
        fm.write_cell(cell_id, request.content)

    content = fm.read_cell(cell_id)
    return CellResponse(
        id=entry.id,
        name=entry.name,
        cell_type=entry.cell_type,
        file=entry.file,
        content=content,
        state=CellState.IDLE,
    )


@router.delete("/{cell_id}")
async def delete_cell(
    cell_id: str,
    fm: FileManager = Depends(get_file_manager),
) -> dict[str, str]:
    try:
        fm.delete_cell(cell_id)
    except CellNotFoundError:
        raise HTTPException(status_code=404, detail=f"Cell not found: {cell_id}")
    return {"status": "ok"}


@router.post("/{cell_id}/move")
async def move_cell(
    cell_id: str,
    request: CellMoveRequest,
    fm: FileManager = Depends(get_file_manager),
) -> dict[str, str]:
    try:
        fm.move_cell(cell_id, request.after_id)
    except CellNotFoundError:
        raise HTTPException(status_code=404, detail=f"Cell not found: {cell_id}")
    return {"status": "ok"}
