"""Notebook manifest endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from lembic.models.cells import CellResponse, CellState
from lembic.models.notebook import NotebookResponse, NotebookSection, NotebookSettings, ReorderRequest
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
                annotation=entry.annotation,
                last_author=change.author.value if change else None,
                last_modified=change.timestamp.isoformat() if change else None,
            )
        )
    return NotebookResponse(cells=cells, sections=manifest.sections)


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


# --- Sections ---


class SectionCreate(BaseModel):
    name: str
    starts_at: str  # cell_id
    ends_at: str | None = None


@router.get("/sections", response_model=list[NotebookSection])
async def list_sections(fm: FileManager = Depends(get_file_manager)) -> list[NotebookSection]:
    manifest = fm.load_manifest()
    return manifest.sections


@router.post("/sections", response_model=NotebookSection, status_code=201)
async def create_section(
    request: SectionCreate,
    fm: FileManager = Depends(get_file_manager),
) -> NotebookSection:
    manifest = fm.load_manifest()
    section = NotebookSection(
        id=fm._generate_unique_section_id(),
        name=request.name,
        starts_at=request.starts_at,
        ends_at=request.ends_at,
    )
    manifest.sections.append(section)
    fm.save_manifest()
    return section


@router.delete("/sections/{section_id}")
async def delete_section(
    section_id: str,
    fm: FileManager = Depends(get_file_manager),
) -> dict[str, str]:
    manifest = fm.load_manifest()
    before = len(manifest.sections)
    manifest.sections = [s for s in manifest.sections if s.id != section_id]
    if len(manifest.sections) == before:
        raise HTTPException(status_code=404, detail=f"Section not found: {section_id}")
    fm.save_manifest()
    return {"status": "ok"}


@router.put("/sections/{section_id}", response_model=NotebookSection)
async def update_section(
    section_id: str,
    updates: dict,
    fm: FileManager = Depends(get_file_manager),
) -> NotebookSection:
    manifest = fm.load_manifest()
    for section in manifest.sections:
        if section.id == section_id:
            if "name" in updates:
                section.name = updates["name"]
            if "collapsed" in updates:
                section.collapsed = updates["collapsed"]
            if "starts_at" in updates:
                section.starts_at = updates["starts_at"]
            if "ends_at" in updates:
                section.ends_at = updates["ends_at"]  # str or None to clear
            fm.save_manifest()
            return section
    raise HTTPException(status_code=404, detail=f"Section not found: {section_id}")
