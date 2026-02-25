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
    """Manages a PTY process with async read/write.

    Uses the event loop's fd monitoring (add_reader) to drain the PTY
    master into an asyncio.Queue, decoupling reads from WebSocket sends
    so the PTY kernel buffer never fills up and blocks the child process.
    """

    def __init__(self) -> None:
        self._master_fd: int | None = None
        self._pid: int | None = None
        self._running = False
        self._output_queue: asyncio.Queue[bytes] = asyncio.Queue()

    async def start(self, command: str = "/bin/bash", cwd: str | None = None) -> None:
        """Start a new PTY process."""
        if self._running:
            return

        master_fd, slave_fd = pty.openpty()

        child_pid = os.fork()
        if child_pid == 0:
            # Child process: close master, use slave for stdio
            os.close(master_fd)
            os.setsid()

            # Set up slave as controlling terminal
            tty_fd = os.open(os.ttyname(slave_fd), os.O_RDWR)
            os.dup2(tty_fd, 0)
            os.dup2(tty_fd, 1)
            os.dup2(tty_fd, 2)
            if tty_fd > 2:
                os.close(tty_fd)
            os.close(slave_fd)

            if cwd:
                os.chdir(cwd)

            env = os.environ.copy()
            env["TERM"] = "xterm-256color"
            env["COLORTERM"] = "truecolor"

            os.execvpe(command, [command], env)
        else:
            # Parent process: close slave, keep master for read/write
            os.close(slave_fd)
            self._master_fd = master_fd
            self._pid = child_pid
            self._running = True

            # Set non-blocking for event-loop integration
            flags = fcntl.fcntl(master_fd, fcntl.F_GETFL)
            fcntl.fcntl(master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

            # Register with event loop — _on_readable fires whenever
            # the master fd has data, draining it into the queue immediately
            loop = asyncio.get_running_loop()
            loop.add_reader(master_fd, self._on_readable)

    def _on_readable(self) -> None:
        """Event loop callback: drain PTY master fd into the output queue."""
        if not self._running or self._master_fd is None:
            return
        try:
            data = os.read(self._master_fd, 65536)
            if data:
                self._output_queue.put_nowait(data)
        except BlockingIOError:
            pass
        except OSError:
            self._running = False

    async def read(self) -> AsyncIterator[bytes]:
        """Async generator yielding data from the PTY output queue."""
        while self._running or not self._output_queue.empty():
            try:
                data = await asyncio.wait_for(self._output_queue.get(), timeout=0.5)
                yield data
            except asyncio.TimeoutError:
                continue

    async def write(self, data: bytes) -> None:
        """Write data to the PTY."""
        if self._master_fd is None:
            return
        while data:
            try:
                written = os.write(self._master_fd, data)
                data = data[written:]
            except BlockingIOError:
                await asyncio.sleep(0.01)
            except OSError:
                break

    async def resize(self, rows: int, cols: int) -> None:
        """Resize the PTY."""
        if self._master_fd is None:
            return
        winsize = struct.pack("HHHH", rows, cols, 0, 0)
        fcntl.ioctl(self._master_fd, termios.TIOCSWINSZ, winsize)

    async def shutdown(self) -> None:
        """Shut down the PTY process."""
        self._running = False
        if self._master_fd is not None:
            try:
                asyncio.get_running_loop().remove_reader(self._master_fd)
            except Exception:
                pass
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
