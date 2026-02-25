"""Notebook manifest endpoints."""

from fastapi import APIRouter, Depends

from lembic.models.cells import CellResponse, CellState
from lembic.models.notebook import NotebookResponse, ReorderRequest
from lembic.server.dependencies import get_file_manager
from lembic.services.file_manager import FileManager

router = APIRouter(prefix="/api/notebook", tags=["notebook"])


@router.get("", response_model=NotebookResponse)
async def get_notebook(fm: FileManager = Depends(get_file_manager)) -> NotebookResponse:
    """Load the full notebook: manifest + all cell contents."""
    manifest = fm.load_manifest()
    cells: list[CellResponse] = []
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
