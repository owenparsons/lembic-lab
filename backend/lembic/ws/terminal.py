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


async def _get_process_args(pid: int) -> str | None:
    """Get the full command line of a process by PID."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "ps", "-p", str(pid), "-o", "args=",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        stdout, _ = await proc.communicate()
        return stdout.decode().strip() if stdout else None
    except OSError:
        return None


async def _poll_foreground(pty: PtyManager, websocket: WebSocket) -> None:
    """Poll the foreground process and notify the frontend when it changes."""
    last_is_claude: bool | None = None
    while pty.running:
        pgid = pty.get_foreground_pgid()
        is_claude = False
        if pgid is not None:
            args = await _get_process_args(pgid)
            is_claude = args is not None and "claude" in args.lower()
        if is_claude != last_is_claude:
            last_is_claude = is_claude
            try:
                await websocket.send_text(json.dumps({
                    "type": "foreground_process",
                    "isClaude": is_claude,
                }))
            except Exception:
                break
        await asyncio.sleep(1)


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

        # Read configured shell from notebook settings
        shell = "/bin/zsh"
        if state.file_manager:
            shell = state.file_manager.load_manifest().settings.shell

        # Disable history expansion so ! in double quotes works normally.
        # Both bash and zsh treat ! as special in interactive mode by default.
        if "zsh" in shell:
            bang_off = ["-o", "NO_BANG_HIST"]
        elif "bash" in shell:
            bang_off = ["+H"]
        else:
            bang_off = []

        # When an init_command is provided, start it directly via shell -c
        # so there's no shell echo of the command.  After it exits, exec
        # replaces the process with an interactive shell for the user.
        if init_command:
            interactive = " ".join([shell] + bang_off + ["-i"])
            args = [shell, "-c", f"{init_command}; exec {interactive}"]
        else:
            args = [shell] + bang_off if bang_off else None

        await pty.start(
            command=shell, cwd=str(state.project_dir), args=args, env=env,
        )
        state.pty_sessions[session_id] = pty

        # Show branded banner before any shell output
        await websocket.send_bytes(TERMINAL_BANNER)
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
    poll_task = asyncio.create_task(_poll_foreground(pty, websocket))

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
        poll_task.cancel()
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
