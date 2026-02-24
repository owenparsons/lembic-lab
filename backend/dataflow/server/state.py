"""Application state container holding all service instances."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dataflow.services.cell_executor import CellExecutor
    from dataflow.services.execution_log import ExecutionLog
    from dataflow.services.file_manager import FileManager
    from dataflow.services.kernel_manager import KernelManager
    from dataflow.services.pty_manager import PtyManager
    from dataflow.ws.manager import ConnectionManager


class AppState:
    """Holds all service instances, initialized during app lifespan."""

    def __init__(self, project_dir: Path) -> None:
        self.project_dir = project_dir
        self.file_manager: FileManager | None = None
        self.kernel_manager: KernelManager | None = None
        self.pty_manager: PtyManager | None = None
        self.execution_log: ExecutionLog | None = None
        self.cell_executor: CellExecutor | None = None
        self.ws_manager: ConnectionManager | None = None
