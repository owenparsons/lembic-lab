"""Cell executor: orchestrates cell execution through the kernel."""

from __future__ import annotations

import asyncio
import time
from typing import Any

from dataflow.models.cells import CellState
from dataflow.models.execution import ExecutionEvent, ExecutionResult, ExecutionStatus
from dataflow.services.execution_log import ExecutionLog
from dataflow.services.file_manager import FileManager
from dataflow.services.kernel_manager import KernelManager
from dataflow.ws.manager import ConnectionManager


class CellExecutor:
    """Orchestrates cell execution: load source → kernel → collect output → log."""

    def __init__(
        self,
        file_manager: FileManager,
        kernel_manager: KernelManager,
        execution_log: ExecutionLog,
        ws_manager: ConnectionManager,
    ) -> None:
        self.fm = file_manager
        self.km = kernel_manager
        self.log = execution_log
        self.ws = ws_manager
        self._lock = asyncio.Lock()

    async def execute_cell(self, cell_id: str) -> ExecutionResult:
        """Execute a single cell and return the result."""
        entry = self.fm.get_cell_entry(cell_id)
        source = self.fm.read_cell(cell_id)

        # Ensure kernel is started
        if not self.km.is_started:
            await self.km.start()

        async with self._lock:
            return await self._run(cell_id, source)

    async def execute_all(self) -> list[ExecutionResult]:
        """Execute all cells in order."""
        manifest = self.fm.load_manifest()
        results = []
        for entry in manifest.cells:
            result = await self.execute_cell(entry.id)
            results.append(result)
        return results

    async def _run(self, cell_id: str, source: str) -> ExecutionResult:
        """Internal: execute code and collect outputs."""
        # Notify running
        await self.ws.broadcast_kernel(
            {"type": "cell_status", "cell_id": cell_id, "state": "running"}
        )

        outputs: list[dict[str, Any]] = []
        error_info: str | None = None
        status = ExecutionStatus.OK
        start_time = time.monotonic()

        async for msg in self.km.execute(source):
            msg_type = msg["msg_type"]
            content = msg["content"]

            if msg_type == "stream":
                ws_msg = {
                    "type": "stream",
                    "cell_id": cell_id,
                    "stream": content.get("name", "stdout"),
                    "text": content.get("text", ""),
                }
                await self.ws.broadcast_kernel(ws_msg)
                outputs.append(ws_msg)

            elif msg_type == "display_data":
                ws_msg = {
                    "type": "display_data",
                    "cell_id": cell_id,
                    "data": content.get("data", {}),
                    "metadata": content.get("metadata", {}),
                }
                await self.ws.broadcast_kernel(ws_msg)
                outputs.append(ws_msg)

            elif msg_type == "execute_result":
                ws_msg = {
                    "type": "execute_result",
                    "cell_id": cell_id,
                    "data": content.get("data", {}),
                    "metadata": content.get("metadata", {}),
                }
                await self.ws.broadcast_kernel(ws_msg)
                outputs.append(ws_msg)

            elif msg_type == "error":
                status = ExecutionStatus.ERROR
                error_info = f"{content.get('ename', '')}: {content.get('evalue', '')}"
                ws_msg = {
                    "type": "error",
                    "cell_id": cell_id,
                    "ename": content.get("ename", ""),
                    "evalue": content.get("evalue", ""),
                    "traceback": content.get("traceback", []),
                }
                await self.ws.broadcast_kernel(ws_msg)
                outputs.append(ws_msg)

        duration_ms = (time.monotonic() - start_time) * 1000

        # Notify completion
        await self.ws.broadcast_kernel({
            "type": "execute_reply",
            "cell_id": cell_id,
            "status": status.value,
            "duration_ms": duration_ms,
        })

        # Log the event
        from datetime import datetime, timezone

        event = ExecutionEvent(
            cell_id=cell_id,
            timestamp=datetime.now(timezone.utc),
            status=status,
            duration_ms=duration_ms,
            error=error_info,
        )
        self.log.append(event)

        return ExecutionResult(
            cell_id=cell_id,
            status=status,
            duration_ms=duration_ms,
            outputs=outputs,
            error=error_info,
        )
