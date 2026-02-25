"""FastAPI dependency injection helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Request

from lembic.server.state import AppState

if TYPE_CHECKING:
    from lembic.services.cell_executor import CellExecutor
    from lembic.services.execution_log import ExecutionLog
    from lembic.services.file_manager import FileManager
    from lembic.services.kernel_manager import KernelManager
    from lembic.services.pty_manager import PtyManager
    from lembic.ws.manager import ConnectionManager


def get_state(request: Request) -> AppState:
    return request.app.state.app_state


def get_file_manager(request: Request) -> FileManager:
    state = get_state(request)
    assert state.file_manager is not None
    return state.file_manager


def get_kernel_manager(request: Request) -> KernelManager:
    state = get_state(request)
    assert state.kernel_manager is not None
    return state.kernel_manager


def get_pty_manager(request: Request) -> PtyManager:
    state = get_state(request)
    assert state.pty_manager is not None
    return state.pty_manager


def get_execution_log(request: Request) -> ExecutionLog:
    state = get_state(request)
    assert state.execution_log is not None
    return state.execution_log


def get_cell_executor(request: Request) -> CellExecutor:
    state = get_state(request)
    if state.cell_executor is None:
        from lembic.services.cell_executor import CellExecutor
        from lembic.services.kernel_manager import KernelManager

        if state.kernel_manager is None:
            state.kernel_manager = KernelManager(str(state.project_dir))
        assert state.file_manager is not None
        assert state.execution_log is not None
        assert state.ws_manager is not None
        state.cell_executor = CellExecutor(
            state.file_manager,
            state.kernel_manager,
            state.execution_log,
            state.ws_manager,
        )
    return state.cell_executor


def get_ws_manager(request: Request) -> ConnectionManager:
    state = get_state(request)
    assert state.ws_manager is not None
    return state.ws_manager
