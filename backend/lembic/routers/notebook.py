"""Notebook manifest endpoints."""

from fastapi import APIRouter, Depends

from lembic.models.cells import CellResponse, CellState
from lembic.models.notebook import NotebookResponse, NotebookSettings, ReorderRequest
from lembic.server.dependencies import get_file_manager, get_state
from lembic.server.state import AppState
from lembic.services.file_manager import FileManager

router = APIRouter(prefix="/api/notebook", tags=["notebook"])


@router.get("", response_model=NotebookResponse)
async def get_notebook(
    fm: FileManager = Depends(get_file_manager),
    state: AppState = Depends(get_state),
) -> NotebookResponse:
    """Load the full notebook: manifest + all cell contents."""
    manifest = fm.load_manifest()
    cells: list[CellResponse] = []
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
    return NotebookResponse(cells=cells)


@router.post("/save")
async def save_notebook(fm: FileManager = Depends(get_file_manager)) -> dict[str, str]:
    """Save the manifest (cells are saved individually via cell endpoints)."""
    fm.save_manifest()
    return {"status": "ok"}


@router.post("/reorder")
async def reorder_cells(
    request: ReorderRequest,
    fm: FileManager = Depends(get_file_manager),
) -> dict[str, str]:
    """Reorder cells in the manifest."""
    fm.reorder_cells(request.cell_ids)
    return {"status": "ok"}


@router.get("/settings", response_model=NotebookSettings)
async def get_settings(fm: FileManager = Depends(get_file_manager)) -> NotebookSettings:
    """Return the current notebook settings."""
    manifest = fm.load_manifest()
    return manifest.settings


@router.put("/settings", response_model=NotebookSettings)
async def update_settings(
    updates: dict,
    fm: FileManager = Depends(get_file_manager),
) -> NotebookSettings:
    """Partially update notebook settings."""
    manifest = fm.load_manifest()
    current = manifest.settings.model_dump()
    current.update(updates)
    manifest.settings = NotebookSettings(**current)
    fm.save_manifest()
    return manifest.settings
