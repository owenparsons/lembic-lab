"""WebSocket connection manager for broadcasting messages."""

from __future__ import annotations

import json
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    """Manages WebSocket connections and broadcasts messages."""

    def __init__(self) -> None:
        self._kernel_connections: list[WebSocket] = []
        self._filewatcher_connections: list[WebSocket] = []

    async def connect_kernel(self, ws: WebSocket) -> None:
        await ws.accept()
        self._kernel_connections.append(ws)

    def disconnect_kernel(self, ws: WebSocket) -> None:
        self._kernel_connections.remove(ws)

    async def connect_filewatcher(self, ws: WebSocket) -> None:
        await ws.accept()
        self._filewatcher_connections.append(ws)

    def disconnect_filewatcher(self, ws: WebSocket) -> None:
        self._filewatcher_connections.remove(ws)

    async def broadcast_kernel(self, message: dict[str, Any]) -> None:
        """Broadcast a JSON message to all kernel WS clients."""
        data = json.dumps(message)
        dead: list[WebSocket] = []
        for ws in self._kernel_connections:
            try:
                await ws.send_text(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._kernel_connections.remove(ws)

    async def broadcast_filewatcher(self, message: dict[str, Any]) -> None:
        """Broadcast a JSON message to all filewatcher WS clients."""
        data = json.dumps(message)
        dead: list[WebSocket] = []
        for ws in self._filewatcher_connections:
            try:
                await ws.send_text(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._filewatcher_connections.remove(ws)
