"""Lembic CLI: init, open, run-cell."""

import subprocess
import sys
import webbrowser
from pathlib import Path

import click


@click.group()
def cli() -> None:
    """Lembic: data science notebook environment."""
    pass


@cli.command()
@click.argument("name")
@click.option("--path", default=None, help="Parent directory (defaults to projects/)")
def init(name: str, path: str | None) -> None:
    """Initialize a new Lembic project."""
    from lembic.filesystem.project_ops import initialize_project

    if path:
        parent = Path(path)
    else:
        parent = Path.home() / "Lembic"

    parent.mkdir(parents=True, exist_ok=True)
    project_dir = parent / name
    initialize_project(project_dir, name)
    click.echo(f"Created Lembic project: {project_dir}")
    click.echo(f"  ./scripts/dev.sh {project_dir}")


@cli.command()
@click.option("--port", default=8000, help="Backend port")
@click.option("--no-browser", is_flag=True, help="Don't open browser")
def open(port: int, no_browser: bool) -> None:
    """Start the Lembic server for the current project."""
    import uvicorn

    project_dir = Path.cwd()
    manifest = project_dir / "notebook.yaml"
    if not manifest.exists():
        click.echo("Error: No notebook.yaml found. Run `lembic init <name>` first.", err=True)
        sys.exit(1)

    import os

    os.environ["LEMBIC_PROJECT_DIR"] = str(project_dir)

    if not no_browser:
        webbrowser.open(f"http://localhost:{port}")

    uvicorn.run(
        "lembic.server.app:create_app",
        factory=True,
        host="0.0.0.0",
        port=port,
        reload=True,
        reload_dirs=[str(Path(__file__).parent)],
    )


@cli.command("run-cell")
@click.argument("cell_id")
def run_cell(cell_id: str) -> None:
    """Execute a cell headlessly (for CC autonomous iteration)."""
    import asyncio

    from lembic.services.cell_executor import CellExecutor
    from lembic.services.execution_log import ExecutionLog
    from lembic.services.file_manager import FileManager
    from lembic.services.kernel_manager import KernelManager
    from lembic.ws.manager import ConnectionManager

    project_dir = Path.cwd()
    fm = FileManager(project_dir)
    km = KernelManager(str(project_dir))
    log = ExecutionLog(project_dir / "execution_log.jsonl")
    ws = ConnectionManager()
    executor = CellExecutor(fm, km, log, ws)

    async def _run() -> None:
        result = await executor.execute_cell(cell_id)
        if result.error:
            click.echo(f"Error: {result.error}", err=True)
            sys.exit(1)
        else:
            click.echo(f"OK ({result.duration_ms:.0f}ms)")
            for output in result.outputs:
                if output.get("type") == "stream":
                    click.echo(output.get("text", ""), nl=False)
        await km.shutdown()

    asyncio.run(_run())
