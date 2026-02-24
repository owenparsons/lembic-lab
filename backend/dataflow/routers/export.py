"""Export endpoints."""

from fastapi import APIRouter, Depends

from dataflow.models.export import ExportFormat, ExportRequest, ExportResult
from dataflow.server.dependencies import get_file_manager
from dataflow.services.exporter import Exporter
from dataflow.services.file_manager import FileManager

router = APIRouter(prefix="/api", tags=["export"])


@router.post("/export", response_model=ExportResult)
async def export_notebook(
    request: ExportRequest,
    fm: FileManager = Depends(get_file_manager),
) -> ExportResult:
    exporter = Exporter(fm)
    return exporter.export(request.format)
