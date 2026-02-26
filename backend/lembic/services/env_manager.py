"""Environment manager: per-project venv management via uv."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil
import sys
from pathlib import Path

import yaml

from lembic.errors import EnvironmentError
from lembic.models.environment import (
    EnvironmentConfig,
    EnvironmentStatus,
    InstallResult,
    PackageInfo,
)

logger = logging.getLogger(__name__)


class EnvironmentManager:
    """Manages a per-project virtual environment using uv."""

    def __init__(self, project_dir: Path) -> None:
        self.project_dir = project_dir
        self._config: EnvironmentConfig | None = None

    # ------------------------------------------------------------------
    # Config persistence (reads/writes 'environment' key in notebook.yaml)
    # ------------------------------------------------------------------

    def _load_config(self) -> EnvironmentConfig:
        if self._config is not None:
            return self._config
        manifest_path = self.project_dir / "notebook.yaml"
        if manifest_path.exists():
            try:
                raw = yaml.safe_load(manifest_path.read_text()) or {}
                env_data = raw.get("environment", {})
                self._config = EnvironmentConfig(**env_data)
            except Exception:
                self._config = EnvironmentConfig()
        else:
            self._config = EnvironmentConfig()
        return self._config

    def _save_config(self, config: EnvironmentConfig) -> None:
        manifest_path = self.project_dir / "notebook.yaml"
        raw: dict = {}
        if manifest_path.exists():
            try:
                raw = yaml.safe_load(manifest_path.read_text()) or {}
            except Exception:
                raw = {}
        raw["environment"] = config.model_dump()
        manifest_path.write_text(
            yaml.dump(raw, default_flow_style=False, sort_keys=False)
        )
        self._config = config

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def venv_path(self) -> Path:
        config = self._load_config()
        p = Path(config.venv_path)
        if p.is_absolute():
            return p
        return self.project_dir / p

    @property
    def python_executable(self) -> Path:
        return self.venv_path / "bin" / "python"

    @property
    def exists(self) -> bool:
        return self.python_executable.exists()

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    async def ensure_env(self) -> None:
        """Create the venv if it doesn't exist, then ensure ipykernel is installed."""
        if self.exists:
            return
        uv = self._find_uv()
        venv = str(self.venv_path)
        await self._run([uv, "venv", venv, "--python", sys.executable])
        logger.info("Created venv at %s", venv)
        # ipykernel is required for the Jupyter kernel to work
        await self._run([
            uv, "pip", "install",
            "--python", str(self.python_executable),
            "ipykernel",
        ])

    async def install(self, packages: list[str]) -> InstallResult:
        """Install packages into the venv (creates it first if needed)."""
        await self.ensure_env()
        uv = self._find_uv()
        python = str(self.python_executable)
        try:
            output = await self._run(
                [uv, "pip", "install", "--python", python, *packages]
            )
            # Update requirements.txt
            await self._freeze_requirements()
            return InstallResult(
                success=True,
                installed=packages,
                output=output,
            )
        except EnvironmentError as e:
            return InstallResult(
                success=False,
                installed=[],
                output=str(e),
            )

    async def uninstall(self, packages: list[str]) -> str:
        """Uninstall packages from the venv."""
        if not self.exists:
            raise EnvironmentError("No virtual environment exists")
        uv = self._find_uv()
        python = str(self.python_executable)
        output = await self._run(
            [uv, "pip", "uninstall", "--python", python, *packages]
        )
        await self._freeze_requirements()
        return output

    async def list_packages(self) -> list[PackageInfo]:
        """List installed packages in the venv."""
        if not self.exists:
            return []
        uv = self._find_uv()
        python = str(self.python_executable)
        try:
            output = await self._run(
                [uv, "pip", "list", "--python", python, "--format", "json"]
            )
            items = json.loads(output)
            return [PackageInfo(name=p["name"], version=p["version"]) for p in items]
        except (json.JSONDecodeError, EnvironmentError):
            return []

    async def get_status(self) -> EnvironmentStatus:
        """Get the current environment status."""
        config = self._load_config()
        if not self.exists:
            return EnvironmentStatus(
                exists=False,
                path=None,
                external=config.external,
                python_version=None,
            )
        # Get python version
        python_version = None
        try:
            output = await self._run(
                [str(self.python_executable), "--version"]
            )
            python_version = output.strip().removeprefix("Python ")
        except EnvironmentError:
            pass
        # Get package count
        packages = await self.list_packages()
        return EnvironmentStatus(
            exists=True,
            path=str(self.venv_path),
            external=config.external,
            python_version=python_version,
            package_count=len(packages),
        )

    def get_shell_env(self) -> dict[str, str]:
        """Return env dict that activates the venv for a child process."""
        env = os.environ.copy()
        venv = str(self.venv_path)
        env["VIRTUAL_ENV"] = venv
        env["PATH"] = os.path.join(venv, "bin") + os.pathsep + env.get("PATH", "")
        env.pop("PYTHONHOME", None)
        return env

    async def set_external(self, path: str) -> None:
        """Point to an external venv."""
        ext = Path(path)
        if not (ext / "bin" / "python").exists():
            raise EnvironmentError(
                f"No Python executable found at {ext / 'bin' / 'python'}"
            )
        config = EnvironmentConfig(venv_path=str(ext), external=True)
        self._save_config(config)

    async def remove(self) -> None:
        """Remove the venv (only if not external)."""
        config = self._load_config()
        if config.external:
            # Just clear the config, don't delete the external venv
            self._save_config(EnvironmentConfig())
            return
        venv = self.venv_path
        if venv.exists():
            shutil.rmtree(venv)
        # Remove requirements.txt too
        req = self.project_dir / "requirements.txt"
        if req.exists():
            req.unlink()
        self._save_config(EnvironmentConfig())

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _find_uv(self) -> str:
        uv = shutil.which("uv")
        if uv is None:
            raise EnvironmentError(
                "uv is not installed or not on PATH. "
                "Install it: https://docs.astral.sh/uv/getting-started/installation/"
            )
        return uv

    async def _run(self, cmd: list[str]) -> str:
        """Run a subprocess and return its stdout."""
        logger.debug("Running: %s", " ".join(cmd))
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(self.project_dir),
        )
        stdout, _ = await proc.communicate()
        output = stdout.decode() if stdout else ""
        if proc.returncode != 0:
            raise EnvironmentError(f"Command failed ({proc.returncode}): {output}")
        return output

    async def _freeze_requirements(self) -> None:
        """Write requirements.txt from current venv state."""
        uv = self._find_uv()
        python = str(self.python_executable)
        try:
            output = await self._run(
                [uv, "pip", "freeze", "--python", python]
            )
            req_path = self.project_dir / "requirements.txt"
            req_path.write_text(output)
        except EnvironmentError:
            logger.warning("Failed to freeze requirements")
