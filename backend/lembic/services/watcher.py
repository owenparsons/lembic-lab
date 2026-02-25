"""File watcher: monitors project directory for external changes."""

from __future__ import annotations

import asyncio
import hashlib
import time
from pathlib import Path
from typing import Callable, Awaitable

from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer


# Paths to ignore
IGNORE_PATTERNS = {
    "__pycache__",
    ".pyc",
    ".DS_Store",
    ".notebook/history",
    "execution_log.jsonl",
    ".git",
    "node_modules",
}


def _should_ignore(path: str) -> bool:
    for pattern in IGNORE_PATTERNS:
        if pattern in path:
            return True
    return False


class DebouncedHandler(FileSystemEventHandler):
    """Debounces file events per-path and checks content hashes to suppress false positives."""

    def __init__(
        self,
        on_change: Callable[[str, str], Awaitable[None]],
        debounce_ms: int = 300,
        loop: asyncio.AbstractEventLoop | None = None,
    ) -> None:
        super().__init__()
        self._on_change = on_change
        self._debounce_ms = debounce_ms
        self._timers: dict[str, asyncio.TimerHandle] = {}
        self._hashes: dict[str, str] = {}
        self._loop = loop

    def _get_loop(self) -> asyncio.AbstractEventLoop:
        if self._loop is None:
            self._loop = asyncio.get_event_loop()
        return self._loop

    def _compute_hash(self, path: str) -> str | None:
        try:
            content = Path(path).read_bytes()
            return hashlib.sha256(content).hexdigest()
        except (OSError, FileNotFoundError):
            return None

    def on_modified(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        self._debounce(event.src_path)

    def on_created(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        self._debounce(event.src_path)

    def _debounce(self, path: str) -> None:
        if _should_ignore(path):
            return

        loop = self._get_loop()

        # Schedule the debounce logic on the event loop thread
        # (watchdog fires events from a background thread, and
        # call_later / TimerHandle.cancel are not thread-safe)
        loop.call_soon_threadsafe(self._schedule, path, loop)

    def _schedule(self, path: str, loop: asyncio.AbstractEventLoop) -> None:
        """Must run on the event loop thread."""
        # Cancel existing timer
        if path in self._timers:
            self._timers[path].cancel()

        def fire() -> None:
            self._timers.pop(path, None)
            # Check content hash
            new_hash = self._compute_hash(path)
            if new_hash is None:
                return
            old_hash = self._hashes.get(path)
            if old_hash == new_hash:
                return  # No actual change
            self._hashes[path] = new_hash
            asyncio.run_coroutine_threadsafe(
                self._on_change(path, new_hash), loop
            )

        self._timers[path] = loop.call_later(
            self._debounce_ms / 1000, fire
        )


class FileWatcher:
    """Watches the project directory for file changes."""

    def __init__(
        self,
        project_dir: Path,
        on_change: Callable[[str, str], Awaitable[None]],
        loop: asyncio.AbstractEventLoop | None = None,
    ) -> None:
        self.project_dir = project_dir
        self._observer: Observer | None = None
        self._handler = DebouncedHandler(on_change, loop=loop)

    def start(self) -> None:
        self._observer = Observer()
        self._observer.schedule(
            self._handler,
            str(self.project_dir),
            recursive=True,
        )
        self._observer.start()

    def stop(self) -> None:
        if self._observer is not None:
            self._observer.stop()
            self._observer.join(timeout=5)
            self._observer = None
