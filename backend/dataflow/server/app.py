"""FastAPI application factory."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dataflow.server.state import AppState
from dataflow.services.execution_log import ExecutionLog
from dataflow.services.file_manager import FileManager
from dataflow.ws.manager import ConnectionManager


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize and tear down application services."""
    state: AppState = app.state.app_state

    # Initialize core services that don't need async setup
    state.file_manager = FileManager(state.project_dir)
    state.execution_log = ExecutionLog(state.project_dir / "execution_log.jsonl")
    state.ws_manager = ConnectionManager()

    # Kernel and PTY managers initialized lazily on first use
    yield

    # Cleanup
    if state.kernel_manager is not None:
        await state.kernel_manager.shutdown()
    if state.pty_manager is not None:
        await state.pty_manager.shutdown()


def create_app(project_dir: str | Path | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    if project_dir is None:
        project_dir = Path(os.environ.get("DATAFLOW_PROJECT_DIR", os.getcwd()))
    else:
        project_dir = Path(project_dir)

    app = FastAPI(
        title="DataFlow",
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
    from dataflow.routers.cells import router as cells_router
    from dataflow.routers.execution import router as execution_router
    from dataflow.routers.notebook import router as notebook_router
    from dataflow.routers.project import router as project_router
    from dataflow.routers.profile import router as profile_router
    from dataflow.routers.variables import router as variables_router

    app.include_router(project_router)
    app.include_router(notebook_router)
    app.include_router(cells_router)
    app.include_router(execution_router)
    app.include_router(variables_router)
    app.include_router(profile_router)

    # Register WebSocket endpoints
    from dataflow.ws.kernel import router as kernel_ws_router
    from dataflow.ws.terminal import router as terminal_ws_router
    from dataflow.ws.filewatcher import router as filewatcher_ws_router

    app.include_router(kernel_ws_router)
    app.include_router(terminal_ws_router)
    app.include_router(filewatcher_ws_router)

    return app
