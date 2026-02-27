"""FastAPI application factory."""

from __future__ import annotations

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from lembic.models.changes import ChangeAuthor
from lembic.server.state import AppState
from lembic.services.change_log import ChangeLog
from lembic.services.env_manager import EnvironmentManager
from lembic.services.execution_log import ExecutionLog
from lembic.services.file_manager import FileManager
from lembic.services.watcher import FileWatcher
from lembic.ws.manager import ConnectionManager

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize and tear down application services."""
    state: AppState = app.state.app_state

    # Initialize core services that don't need async setup
    state.file_manager = FileManager(state.project_dir)
    state.env_manager = EnvironmentManager(state.project_dir)
    state.execution_log = ExecutionLog(state.project_dir / "execution_log.jsonl")
    state.change_log = ChangeLog(state.project_dir / ".notebook" / "changes.jsonl")
    state.ws_manager = ConnectionManager()

    # File watcher for live-reload
    loop = asyncio.get_running_loop()
    file_manager = state.file_manager
    ws_manager = state.ws_manager
    cells_dir = state.project_dir / "cells"

    async def on_file_change(path: str, new_hash: str) -> None:
        if path.endswith("notebook.yaml"):
            file_manager.invalidate_manifest()
            try:
                manifest = file_manager.load_manifest()
                await ws_manager.broadcast_filewatcher(
                    {
                        "type": "manifest_modified",
                        "manifest": manifest.model_dump(),
                    }
                )
            except Exception:
                logger.exception("Error broadcasting manifest change")
        elif cells_dir.as_posix() in path:
            # Extract cell ID from filename like "abc123_my_cell.py"
            filename = Path(path).stem
            cell_id = filename.split("_")[0]
            try:
                content = Path(path).read_text()
            except OSError:
                return

            # Log change — skip if this was a recent API write (de-dup)
            api_hash = state._api_write_hashes.pop(cell_id, None)
            if api_hash != new_hash and state.change_log is not None:
                state.change_log.append(cell_id, ChangeAuthor.EXTERNAL, new_hash)

            await ws_manager.broadcast_filewatcher(
                {
                    "type": "cell_modified",
                    "cell_id": cell_id,
                    "new_content": content,
                    "new_hash": new_hash,
                }
            )

    state.file_watcher = FileWatcher(state.project_dir, on_file_change, loop=loop)
    state.file_watcher.start()

    # Kernel and PTY managers initialized lazily on first use
    yield

    # Cleanup
    if state.file_watcher is not None:
        state.file_watcher.stop()
    if state.kernel_manager is not None:
        await state.kernel_manager.shutdown()
    for pty_session in state.pty_sessions.values():
        await pty_session.shutdown()
    state.pty_sessions.clear()


def create_app(project_dir: str | Path | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    if project_dir is None:
        project_dir = Path(os.environ.get("LEMBIC_PROJECT_DIR", os.getcwd()))
    else:
        project_dir = Path(project_dir)

    app = FastAPI(
        title="Lembic",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Store state on app
    app.state.app_state = AppState(project_dir)

    # CORS for dev (Vite on :5173 → backend on :8000)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    from lembic.routers.cells import router as cells_router
    from lembic.routers.execution import router as execution_router
    from lembic.routers.notebook import router as notebook_router
    from lembic.routers.project import router as project_router
    from lembic.routers.export import router as export_router
    from lembic.routers.profile import router as profile_router
    from lembic.routers.variables import router as variables_router
    from lembic.routers.environment import router as environment_router

    app.include_router(project_router)
    app.include_router(notebook_router)
    app.include_router(cells_router)
    app.include_router(execution_router)
    app.include_router(variables_router)
    app.include_router(profile_router)
    app.include_router(export_router)
    app.include_router(environment_router)

    # Register WebSocket endpoints
    from lembic.ws.kernel import router as kernel_ws_router
    from lembic.ws.terminal import router as terminal_ws_router
    from lembic.ws.filewatcher import router as filewatcher_ws_router

    app.include_router(kernel_ws_router)
    app.include_router(terminal_ws_router)
    app.include_router(filewatcher_ws_router)

    return app
