"""Cell CRUD endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from lembic.errors import CellNotFoundError
from lembic.models.cells import (
    CellCreate,
    CellMoveRequest,
    CellResponse,
    CellState,
    CellUpdate,
)
from lembic.models.changes import ChangeAuthor
from lembic.server.dependencies import get_file_manager, get_state
from lembic.server.state import AppState
from lembic.services.file_manager import FileManager

router = APIRouter(prefix="/api/cells", tags=["cells"])


@router.get("", response_model=list[CellResponse])
async def list_cells(
    fm: FileManager = Depends(get_file_manager),
    state: AppState = Depends(get_state),
) -> list[CellResponse]:
    manifest = fm.load_manifest()
    cells = []
    for entry in manifest.cells:
        content = fm.read_cell(entry.id)
        change = state.change_log.last_change_for_cell(entry.id) if state.change_log else None
        cells.append(
            CellResponse(
                id=entry.id,
                name=entry.name,
                cell_type=entry.cell_type,
                file=entry.file,
                content=content,
                state=CellState.IDLE,
                last_author=change.author.value if change else None,
                last_modified=change.timestamp.isoformat() if change else None,
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
    state: AppState = Depends(get_state),
) -> CellResponse:
    try:
        entry = fm.get_cell_entry(cell_id)
    except CellNotFoundError:
        raise HTTPException(status_code=404, detail=f"Cell not found: {cell_id}")
    content = fm.read_cell(cell_id)
    change = state.change_log.last_change_for_cell(cell_id) if state.change_log else None
    return CellResponse(
        id=entry.id,
        name=entry.name,
        cell_type=entry.cell_type,
        file=entry.file,
        content=content,
        state=CellState.IDLE,
        last_author=change.author.value if change else None,
        last_modified=change.timestamp.isoformat() if change else None,
    )


@router.put("/{cell_id}", response_model=CellResponse)
async def update_cell(
    cell_id: str,
    request: CellUpdate,
    fm: FileManager = Depends(get_file_manager),
    state: AppState = Depends(get_state),
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
        # Record user change and set de-dup hash so watcher skips it
        content_hash = fm.cell_content_hash(cell_id)
        state._api_write_hashes[cell_id] = content_hash
        if state.change_log is not None:
            state.change_log.append(cell_id, ChangeAuthor.USER, content_hash)

    content = fm.read_cell(cell_id)
    change = state.change_log.last_change_for_cell(cell_id) if state.change_log else None
    return CellResponse(
        id=entry.id,
        name=entry.name,
        cell_type=entry.cell_type,
        file=entry.file,
        content=content,
        state=CellState.IDLE,
        last_author=change.author.value if change else None,
        last_modified=change.timestamp.isoformat() if change else None,
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


@router.get("/{cell_id}/history", response_model=list[dict[str, Any]])
async def cell_history(
    cell_id: str,
    state: AppState = Depends(get_state),
) -> list[dict[str, Any]]:
    """Get version history for a cell."""
    from lembic.services.version_history import VersionHistory

    vh = VersionHistory(state.project_dir)
    return vh.list_versions(cell_id)


@router.get("/{cell_id}/history/{timestamp}")
async def cell_history_version(
    cell_id: str,
    timestamp: int,
    state: AppState = Depends(get_state),
) -> dict[str, Any]:
    """Get a specific historical version of a cell."""
    from lembic.services.version_history import VersionHistory

    vh = VersionHistory(state.project_dir)
    content = vh.get_version(cell_id, timestamp)
    if content is None:
        raise HTTPException(status_code=404, detail="Version not found")
    return {"cell_id": cell_id, "timestamp": timestamp, "content": content}
