"""FastAPI dependency injection helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import Request

from dataflow.server.state import AppState

if TYPE_CHECKING:
    from dataflow.services.cell_executor import CellExecutor
    from dataflow.services.execution_log import ExecutionLog
    from dataflow.services.file_manager import FileManager
    from dataflow.services.kernel_manager import KernelManager
    from dataflow.services.pty_manager import PtyManager
    from dataflow.ws.manager import ConnectionManager


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
    assert state.cell_executor is not None
    return state.cell_executor


def get_ws_manager(request: Request) -> ConnectionManager:
    state = get_state(request)
    assert state.ws_manager is not None
    return state.ws_manager
