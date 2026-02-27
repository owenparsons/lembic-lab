"""WebSocket endpoint for terminal PTY communication."""

import asyncio
import json
import logging

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect

from lembic.server.state import AppState
from lembic.services.pty_manager import PtyManager
from lembic.templates.terminal_banner import TERMINAL_BANNER

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/terminal/{session_id}")
async def terminal_ws(websocket: WebSocket, session_id: str) -> None:
    await websocket.accept()
    state: AppState = websocket.app.state.app_state

    init_command = websocket.query_params.get("init_command")

    # Lazily create PTY for this session
    if session_id not in state.pty_sessions:
        pty = PtyManager()
        # Activate venv in terminal if environment exists
        env = None
        if state.env_manager and state.env_manager.exists:
            env = state.env_manager.get_shell_env()
        await pty.start(cwd=str(state.project_dir), env=env)
        state.pty_sessions[session_id] = pty

        # Show branded banner before any shell output
        await websocket.send_bytes(TERMINAL_BANNER)

        # Run initial command if provided (only on first creation)
        if init_command:
            await pty.write((init_command + "\n").encode("utf-8"))
    else:
        pty = state.pty_sessions[session_id]

    async def read_pty() -> None:
        """Forward PTY output to WebSocket."""
        try:
            async for data in pty.read():
                await websocket.send_bytes(data)
        except Exception:
            pass
        # Shell process has exited — notify the frontend
        try:
            await websocket.send_text(json.dumps({"type": "shell_exited"}))
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
    except (WebSocketDisconnect, RuntimeError):
        pass
    finally:
        read_task.cancel()
        logger.info("Terminal WebSocket disconnected (session=%s)", session_id)


@router.delete("/api/terminal/{session_id}")
async def delete_terminal(session_id: str, request: Request) -> dict[str, str]:
    """Shut down and remove a PTY session."""
    state: AppState = request.app.state.app_state
    pty = state.pty_sessions.pop(session_id, None)
    if pty is not None:
        await pty.shutdown()
        logger.info("Terminal session deleted: %s", session_id)
        return {"status": "deleted"}
    return {"status": "not_found"}
