"""Kernel manager: wraps jupyter_client for async kernel operations."""

from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator

from jupyter_client import AsyncKernelManager as JupyterAsyncKernelManager

from dataflow.errors import KernelNotStartedError


class KernelManager:
    """Manages a Jupyter kernel for code execution."""

    def __init__(self, project_dir: str) -> None:
        self.project_dir = project_dir
        self._km: JupyterAsyncKernelManager | None = None
        self._kc: Any = None  # AsyncKernelClient
        self._started = False

    @property
    def is_started(self) -> bool:
        return self._started

    async def start(self) -> None:
        """Start the kernel."""
        if self._started:
            return

        self._km = JupyterAsyncKernelManager()
        await self._km.start_kernel(cwd=self.project_dir)
        self._kc = self._km.client()
        self._kc.start_channels()

        # Wait for kernel ready
        try:
            await asyncio.wait_for(self._kc.wait_for_ready(), timeout=30)
        except asyncio.TimeoutError:
            await self.shutdown()
            raise

        self._started = True

        # Run startup code
        await self._run_startup()

    async def _run_startup(self) -> None:
        """Inject startup code into the kernel."""
        startup = [
            "import sys",
            f"sys.path.insert(0, {self.project_dir!r})",
            "%matplotlib inline",
            "import warnings; warnings.filterwarnings('ignore')",
        ]
        for code in startup:
            try:
                msg_id = self._kc.execute(code, silent=True)
                # Drain the reply
                async for _ in self._iter_messages(msg_id):
                    pass
            except Exception:
                pass

    def _ensure_started(self) -> None:
        if not self._started or self._kc is None:
            raise KernelNotStartedError("Kernel not started")

    async def execute(self, code: str) -> AsyncIterator[dict[str, Any]]:
        """Execute code and yield IOPub messages."""
        self._ensure_started()
        msg_id = self._kc.execute(code)
        async for msg in self._iter_messages(msg_id):
            yield msg

    async def _iter_messages(self, msg_id: str) -> AsyncIterator[dict[str, Any]]:
        """Iterate over IOPub messages for a given execution."""
        while True:
            try:
                msg = await asyncio.wait_for(
                    self._kc.get_iopub_msg(),
                    timeout=60,
                )
            except asyncio.TimeoutError:
                break

            if msg["parent_header"].get("msg_id") != msg_id:
                continue

            msg_type = msg["header"]["msg_type"]
            content = msg["content"]

            yield {"msg_type": msg_type, "content": content}

            if msg_type in ("execute_reply", "status"):
                if content.get("execution_state") == "idle":
                    break

    async def interrupt(self) -> None:
        """Interrupt the running kernel."""
        self._ensure_started()
        assert self._km is not None
        await self._km.interrupt_kernel()

    async def restart(self) -> None:
        """Restart the kernel."""
        self._ensure_started()
        assert self._km is not None
        await self._km.restart_kernel()
        assert self._kc is not None
        await asyncio.wait_for(self._kc.wait_for_ready(), timeout=30)
        await self._run_startup()

    async def get_variables(self) -> list[dict[str, Any]]:
        """Introspect kernel namespace for variable information."""
        self._ensure_started()
        code = """
import json as _json_
_vars_ = {}
for _name_ in dir():
    if not _name_.startswith('_'):
        _obj_ = eval(_name_)
        _info_ = {'name': _name_, 'var_type': type(_obj_).__name__}
        try:
            if hasattr(_obj_, 'shape'):
                _info_['shape'] = str(_obj_.shape)
            if hasattr(_obj_, '__len__'):
                _info_['preview'] = str(_obj_)[:200]
            else:
                _info_['preview'] = repr(_obj_)[:200]
        except Exception:
            _info_['preview'] = '<error>'
        _vars_[_name_] = _info_
print(_json_.dumps(list(_vars_.values())))
del _json_, _vars_, _name_, _obj_, _info_
"""
        import json

        result_text = ""
        async for msg in self.execute(code):
            if msg["msg_type"] == "stream" and msg["content"].get("name") == "stdout":
                result_text += msg["content"].get("text", "")

        try:
            return json.loads(result_text)
        except (json.JSONDecodeError, ValueError):
            return []

    async def shutdown(self) -> None:
        """Shut down the kernel."""
        if self._kc is not None:
            self._kc.stop_channels()
            self._kc = None
        if self._km is not None:
            await self._km.shutdown_kernel(now=True)
            self._km = None
        self._started = False
