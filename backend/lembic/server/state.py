"""Application state container holding all service instances."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lembic.services.cell_executor import CellExecutor
    from lembic.services.env_manager import EnvironmentManager
    from lembic.services.execution_log import ExecutionLog
    from lembic.services.file_manager import FileManager
    from lembic.services.kernel_manager import KernelManager
    from lembic.services.pty_manager import PtyManager
    from lembic.services.watcher import FileWatcher
    from lembic.ws.manager import ConnectionManager


class AppState:
    """Holds all service instances, initialized during app lifespan."""

    def __init__(self, project_dir: Path) -> None:
        self.project_dir = project_dir
        self.file_manager: FileManager | None = None
        self.env_manager: EnvironmentManager | None = None
        self.kernel_manager: KernelManager | None = None
        self.pty_sessions: dict[str, PtyManager] = {}
        self.execution_log: ExecutionLog | None = None
        self.cell_executor: CellExecutor | None = None
        self.ws_manager: ConnectionManager | None = None
        self.file_watcher: FileWatcher | None = None
