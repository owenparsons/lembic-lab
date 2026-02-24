"""PTY manager: manages a pseudo-terminal for the terminal pane."""

from __future__ import annotations

import asyncio
import fcntl
import os
import pty
import signal
import struct
import termios
from typing import AsyncIterator


class PtyManager:
    """Manages a PTY process with async read/write."""

    def __init__(self) -> None:
        self._master_fd: int | None = None
        self._pid: int | None = None
        self._running = False

    async def start(self, command: str = "/bin/bash", cwd: str | None = None) -> None:
        """Start a new PTY process."""
        if self._running:
            return

        pid, master_fd = pty.openpty()

        child_pid = os.fork()
        if child_pid == 0:
            # Child process
            os.close(master_fd)
            os.setsid()

            # Set up slave as controlling terminal
            slave_fd = os.open(os.ttyname(pid), os.O_RDWR)
            os.dup2(slave_fd, 0)
            os.dup2(slave_fd, 1)
            os.dup2(slave_fd, 2)
            if slave_fd > 2:
                os.close(slave_fd)
            os.close(pid)

            if cwd:
                os.chdir(cwd)

            env = os.environ.copy()
            env["TERM"] = "xterm-256color"
            env["COLORTERM"] = "truecolor"

            os.execvpe(command, [command], env)
        else:
            # Parent process
            os.close(pid)
            self._master_fd = master_fd
            self._pid = child_pid
            self._running = True

            # Set non-blocking
            flags = fcntl.fcntl(master_fd, fcntl.F_GETFL)
            fcntl.fcntl(master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

    async def read(self) -> AsyncIterator[bytes]:
        """Async generator yielding data from the PTY."""
        if self._master_fd is None:
            return

        loop = asyncio.get_event_loop()
        while self._running:
            try:
                data = await loop.run_in_executor(None, self._blocking_read)
                if data:
                    yield data
            except OSError:
                break

    def _blocking_read(self) -> bytes:
        """Read from PTY with a short timeout."""
        if self._master_fd is None:
            return b""
        import select

        ready, _, _ = select.select([self._master_fd], [], [], 0.1)
        if ready:
            try:
                return os.read(self._master_fd, 4096)
            except OSError:
                self._running = False
                return b""
        return b""

    async def write(self, data: bytes) -> None:
        """Write data to the PTY."""
        if self._master_fd is None:
            return
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, os.write, self._master_fd, data)

    async def resize(self, rows: int, cols: int) -> None:
        """Resize the PTY."""
        if self._master_fd is None:
            return
        winsize = struct.pack("HHHH", rows, cols, 0, 0)
        fcntl.ioctl(self._master_fd, termios.TIOCSWINSZ, winsize)

    async def shutdown(self) -> None:
        """Shut down the PTY process."""
        self._running = False
        if self._pid is not None:
            try:
                os.kill(self._pid, signal.SIGTERM)
                os.waitpid(self._pid, 0)
            except (OSError, ChildProcessError):
                pass
            self._pid = None
        if self._master_fd is not None:
            try:
                os.close(self._master_fd)
            except OSError:
                pass
            self._master_fd = None
