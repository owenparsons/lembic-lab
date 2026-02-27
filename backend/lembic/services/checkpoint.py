"""Checkpoint manager: git-based automatic snapshots."""

from __future__ import annotations

import logging
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Checkpoint:
    hash: str
    timestamp: str
    message: str


class CheckpointManager:
    """Creates and manages git-based checkpoints."""

    COOLDOWN_SECONDS = 30
    PREFIX = "lembic: auto-checkpoint"

    def __init__(self, project_dir: Path) -> None:
        self.project_dir = project_dir
        self._last_checkpoint_time: float = 0
        self._is_git_repo: bool | None = None

    @property
    def is_git_repo(self) -> bool:
        if self._is_git_repo is None:
            self._is_git_repo = (self.project_dir / ".git").is_dir()
        return self._is_git_repo

    def _git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=self.project_dir,
            capture_output=True,
            text=True,
            timeout=10,
        )

    def create_checkpoint(self, reason: str = "") -> str | None:
        """Create a checkpoint commit. Returns commit hash or None if skipped."""
        if not self.is_git_repo:
            return None

        # Cooldown check
        now = time.time()
        if now - self._last_checkpoint_time < self.COOLDOWN_SECONDS:
            return None

        # Stage all changes
        self._git("add", "-A")

        # Check if there's anything to commit
        result = self._git("diff", "--cached", "--quiet")
        if result.returncode == 0:
            return None  # Nothing staged

        msg = f"{self.PREFIX} {reason}".strip()
        result = self._git("commit", "-m", msg)
        if result.returncode != 0:
            logger.warning("Checkpoint commit failed: %s", result.stderr)
            return None

        self._last_checkpoint_time = now

        # Get the commit hash
        result = self._git("rev-parse", "HEAD")
        return result.stdout.strip() if result.returncode == 0 else None

    def list_checkpoints(self, limit: int = 20) -> list[Checkpoint]:
        """List recent auto-checkpoints."""
        if not self.is_git_repo:
            return []

        result = self._git(
            "log",
            f"--grep={self.PREFIX}",
            f"-{limit}",
            "--format=%H|%ai|%s",
        )
        if result.returncode != 0:
            return []

        checkpoints = []
        for line in result.stdout.strip().splitlines():
            if not line:
                continue
            parts = line.split("|", 2)
            if len(parts) == 3:
                checkpoints.append(Checkpoint(hash=parts[0], timestamp=parts[1], message=parts[2]))
        return checkpoints

    def revert_to_checkpoint(self, commit_hash: str) -> bool:
        """Revert working tree to a checkpoint. Returns True on success."""
        if not self.is_git_repo:
            return False

        result = self._git("checkout", commit_hash, "--", ".")
        if result.returncode != 0:
            logger.warning("Checkout failed: %s", result.stderr)
            return False

        # Stage and commit the revert
        self._git("add", "-A")
        result = self._git("commit", "-m", f"lembic: revert to checkpoint {commit_hash[:8]}")
        return result.returncode == 0
