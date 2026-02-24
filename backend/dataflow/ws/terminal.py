"""WebSocket endpoint for terminal PTY communication."""

import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from dataflow.server.state import AppState
from dataflow.services.pty_manager import PtyManager

router = APIRouter()


@router.websocket("/ws/terminal")
async def terminal_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    state: AppState = websocket.app.state.app_state

    # Lazily start PTY if needed
    if state.pty_manager is None:
        state.pty_manager = PtyManager()
        await state.pty_manager.start(cwd=str(state.project_dir))

    pty = state.pty_manager

    async def read_pty() -> None:
        """Forward PTY output to WebSocket."""
        try:
            async for data in pty.read():
                await websocket.send_bytes(data)
        except Exception:
            pass

    read_task = asyncio.create_task(read_pty())

    try:
        while True:
            message = await websocket.receive()
            if "bytes" in message:
                await pty.write(message["bytes"])
            elif "text" in message:
                try:
                    msg = json.loads(message["text"])
                    if msg.get("type") == "resize":
                        await pty.resize(msg["rows"], msg["cols"])
                    elif msg.get("type") == "inject":
                        text = msg.get("message", "")
                        await pty.write(text.encode("utf-8"))
                except (json.JSONDecodeError, KeyError):
                    pass
    except WebSocketDisconnect:
        read_task.cancel()
