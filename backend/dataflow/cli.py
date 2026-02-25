"""DataFlow CLI: init, open, run-cell."""

import subprocess
import sys
import webbrowser
from pathlib import Path

import click


@click.group()
def cli() -> None:
    """DataFlow: data science notebook environment."""
    pass


@cli.command()
@click.argument("name")
@click.option("--path", default=None, help="Parent directory (defaults to projects/)")
def init(name: str, path: str | None) -> None:
    """Initialize a new DataFlow project."""
    from dataflow.filesystem.project_ops import initialize_project

    if path:
        parent = Path(path)
    else:
        # Default to projects/ directory at the repo root
        parent = Path(__file__).resolve().parent.parent.parent / "projects"

    parent.mkdir(parents=True, exist_ok=True)
    project_dir = parent / name
    initialize_project(project_dir, name)
    click.echo(f"Created DataFlow project: {project_dir}")
    click.echo(f"  ./scripts/dev.sh {project_dir}")


@cli.command()
@click.option("--port", default=8000, help="Backend port")
@click.option("--no-browser", is_flag=True, help="Don't open browser")
def open(port: int, no_browser: bool) -> None:
    """Start the DataFlow server for the current project."""
    import uvicorn

    project_dir = Path.cwd()
    manifest = project_dir / "dataflow.yaml"
    if not manifest.exists():
        click.echo("Error: No dataflow.yaml found. Run `dataflow init <name>` first.", err=True)
        sys.exit(1)

    import os

    os.environ["DATAFLOW_PROJECT_DIR"] = str(project_dir)

    if not no_browser:
        webbrowser.open(f"http://localhost:{port}")

    uvicorn.run(
        "dataflow.server.app:create_app",
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

    from dataflow.services.cell_executor import CellExecutor
    from dataflow.services.execution_log import ExecutionLog
    from dataflow.services.file_manager import FileManager
    from dataflow.services.kernel_manager import KernelManager
    from dataflow.ws.manager import ConnectionManager

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
