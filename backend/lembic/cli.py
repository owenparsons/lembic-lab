"""Lembic CLI: notebook management commands."""

import re
import subprocess
import sys
import webbrowser
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import click


class OverlapAction(Enum):
    TRIM_END = "trim_end"
    REMOVE = "remove"
    TRIM_START = "trim_start"


@dataclass
class OverlapAdjustment:
    section_id: str
    section_name: str
    action: OverlapAction
    new_boundary: str | None = None  # new cell_id for the trimmed boundary
    description: str = ""            # human-readable explanation


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


@cli.command("gen-cell")
def gen_cell() -> None:
    """Generate a cell ID and random name. Output: {id} {name}"""
    import uuid

    from lembic.services.file_manager import FileManager
    from lembic.services.name_generator import generate_name

    project_dir = Path.cwd()
    manifest = project_dir / "notebook.yaml"
    if manifest.exists():
        fm = FileManager(project_dir)
        cell_id = fm._generate_unique_cell_id()
        existing = {c.name for c in fm.load_manifest().cells}
    else:
        cell_id = uuid.uuid4().hex[:8]
        existing = set()

    name = generate_name(existing)
    click.echo(f"{cell_id} {name}")


# ---------------------------------------------------------------------------
# Cell management commands
# ---------------------------------------------------------------------------


@cli.command("add-cell")
@click.option("--type", "cell_type", default="code", type=click.Choice(["code", "markdown"]), help="Cell type")
@click.option("--name", default=None, help="Cell name (auto-generated if omitted)")
@click.option("--after", "after_id", default=None, help="Insert after this cell ID")
@click.option("--content", default="", help="Initial cell content")
def add_cell(cell_type: str, name: str | None, after_id: str | None, content: str) -> None:
    """Create a cell: file + manifest entry in one step."""
    from lembic.models.cells import CellType
    from lembic.services.file_manager import FileManager

    project_dir = Path.cwd()
    fm = FileManager(project_dir)
    ct = CellType.CODE if cell_type == "code" else CellType.MARKDOWN
    entry = fm.create_cell(cell_type=ct, name=name, content=content, after_id=after_id)
    click.echo(f"{entry.id} {entry.name} {entry.file}")


@cli.command("delete-cell")
@click.argument("cell_id")
def delete_cell(cell_id: str) -> None:
    """Delete a cell (file + manifest entry)."""
    from lembic.services.file_manager import FileManager

    project_dir = Path.cwd()
    fm = FileManager(project_dir)
    entry = fm.get_cell_entry(cell_id)
    fm.delete_cell(cell_id)
    click.echo(f"Deleted {entry.id} ({entry.name})")


@cli.command("move-cell")
@click.argument("cell_id")
@click.option("--after", "after_id", default=None, help="Place after this cell ID")
@click.option("--to-start", is_flag=True, help="Move to the beginning")
def move_cell(cell_id: str, after_id: str | None, to_start: bool) -> None:
    """Move a cell to a new position in the notebook."""
    from lembic.services.file_manager import FileManager

    if not after_id and not to_start:
        click.echo("Error: specify --after CELL_ID or --to-start", err=True)
        sys.exit(1)

    project_dir = Path.cwd()
    fm = FileManager(project_dir)
    target = None if to_start else after_id
    fm.move_cell(cell_id, target)
    entry = fm.get_cell_entry(cell_id)
    click.echo(f"Moved {entry.id} ({entry.name})")


# ---------------------------------------------------------------------------
# Status command
# ---------------------------------------------------------------------------


@cli.command("status")
def status() -> None:
    """Show notebook state: cells, execution states, and warnings."""
    from lembic.services.execution_log import ExecutionLog
    from lembic.services.file_manager import FileManager
    from lembic.services.warning_engine import compute_warnings

    project_dir = Path.cwd()
    fm = FileManager(project_dir)
    manifest = fm.load_manifest()

    if not manifest.cells:
        click.echo(f"Notebook: {manifest.name or project_dir.name}")
        click.echo("Cells: 0")
        return

    log = ExecutionLog(project_dir / "execution_log.jsonl")
    events = log.read_all()
    states, warnings = compute_warnings(manifest, events, fm)

    click.echo(f"Notebook: {manifest.name or project_dir.name}")
    click.echo(f"Cells: {len(manifest.cells)}")
    click.echo()

    for i, cell in enumerate(manifest.cells, 1):
        state = states.get(cell.id, "idle")
        if hasattr(state, "value"):
            state = state.value
        type_label = cell.cell_type.value
        click.echo(f"  {i}. [{cell.id}] {cell.name:<20s} ({type_label:<10s}) [{state}]")

    if warnings:
        click.echo()
        click.echo("Warnings:")
        for w in warnings:
            click.echo(f"  ! {w}")


# ---------------------------------------------------------------------------
# Run cell (with full output capture)
# ---------------------------------------------------------------------------


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text."""
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


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
                msg_type = output.get("type")
                if msg_type == "stream":
                    click.echo(output.get("text", ""), nl=False)
                elif msg_type in ("execute_result", "display_data"):
                    data = output.get("data", {})
                    text = data.get("text/plain", "")
                    if text:
                        click.echo(text)
                elif msg_type == "error":
                    tb_lines = output.get("traceback", [])
                    for line in tb_lines:
                        click.echo(_strip_ansi(line), err=True)
        await km.shutdown()

    asyncio.run(_run())


# ---------------------------------------------------------------------------
# Variables command
# ---------------------------------------------------------------------------


@cli.command("variables")
@click.option("--port", default=8000, help="Server port")
def variables(port: int) -> None:
    """Show kernel variables (requires running server)."""
    import json
    import urllib.request

    url = f"http://localhost:{port}/api/variables"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read())
    except Exception as exc:
        click.echo(f"Error: could not reach server at port {port} ({exc})", err=True)
        sys.exit(1)

    if not data:
        click.echo("No variables in kernel.")
        return

    # Compute column widths
    name_w = max(len(v["name"]) for v in data)
    type_w = max(len(v["var_type"]) for v in data)
    name_w = max(name_w, 4)
    type_w = max(type_w, 4)

    click.echo(f"{'Name':<{name_w}}  {'Type':<{type_w}}  Preview")
    click.echo(f"{'-' * name_w}  {'-' * type_w}  {'-' * 40}")
    for v in data:
        preview = v.get("preview", "")
        if len(preview) > 60:
            preview = preview[:57] + "..."
        click.echo(f"{v['name']:<{name_w}}  {v['var_type']:<{type_w}}  {preview}")


# ---------------------------------------------------------------------------
# Change log command
# ---------------------------------------------------------------------------


@cli.command("log")
@click.option("--cell", "cell_id", default=None, help="Filter by cell ID")
@click.option("--limit", default=20, help="Max entries to show")
def log(cell_id: str | None, limit: int) -> None:
    """Show recent cell changes with author attribution."""
    from lembic.services.change_log import ChangeLog
    from lembic.services.file_manager import FileManager

    project_dir = Path.cwd()
    cl = ChangeLog(project_dir / ".notebook" / "changes.jsonl")
    fm = FileManager(project_dir)
    manifest = fm.load_manifest()
    names = {c.id: c.name for c in manifest.cells}

    events = cl.read_all()
    if cell_id:
        events = [e for e in events if e.cell_id == cell_id]

    events = events[-limit:]

    if not events:
        click.echo("No changes recorded.")
        return

    for event in reversed(events):
        ts = event.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        name = names.get(event.cell_id, event.cell_id)
        click.echo(f"  {ts}  {name:<20s}  {event.author.value}")


# ---------------------------------------------------------------------------
# Checkpoint commands
# ---------------------------------------------------------------------------


@cli.group("checkpoints")
def checkpoints_group() -> None:
    """Manage auto-checkpoints."""
    pass


@checkpoints_group.command("list")
@click.option("--limit", default=20, help="Max checkpoints to show")
def checkpoints_list(limit: int) -> None:
    """List recent auto-checkpoints."""
    from lembic.services.checkpoint import CheckpointManager

    project_dir = Path.cwd()
    cm = CheckpointManager(project_dir)

    if not cm.is_git_repo:
        click.echo("Not a git repository — checkpoints disabled.")
        return

    cps = cm.list_checkpoints(limit)
    if not cps:
        click.echo("No checkpoints found.")
        return

    for cp in cps:
        click.echo(f"  {cp.hash[:8]}  {cp.timestamp}  {cp.message}")


@checkpoints_group.command("revert")
@click.argument("commit_hash")
def checkpoints_revert(commit_hash: str) -> None:
    """Revert to a checkpoint."""
    from lembic.services.checkpoint import CheckpointManager

    project_dir = Path.cwd()
    cm = CheckpointManager(project_dir)

    if not cm.is_git_repo:
        click.echo("Not a git repository — checkpoints disabled.", err=True)
        sys.exit(1)

    success = cm.revert_to_checkpoint(commit_hash)
    if success:
        click.echo(f"Reverted to checkpoint {commit_hash[:8]}")
    else:
        click.echo(f"Failed to revert to {commit_hash[:8]}", err=True)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Annotation command
# ---------------------------------------------------------------------------


@cli.command("annotate")
@click.argument("cell_id")
@click.argument("text", required=False)
@click.option("--style", default="info", type=click.Choice(["info", "warning", "success", "error"]))
@click.option("--clear", is_flag=True, help="Remove the annotation")
def annotate(cell_id: str, text: str | None, style: str, clear: bool) -> None:
    """Add or remove an annotation on a cell."""
    from lembic.models.cells import CellAnnotation
    from lembic.services.file_manager import FileManager

    project_dir = Path.cwd()
    fm = FileManager(project_dir)
    entry = fm.get_cell_entry(cell_id)

    if clear:
        entry.annotation = None
        fm.save_manifest()
        click.echo(f"Cleared annotation on {entry.name}")
    elif text:
        entry.annotation = CellAnnotation(text=text, style=style)
        fm.save_manifest()
        click.echo(f"Annotated {entry.name}: [{style}] {text}")
    else:
        click.echo("Error: provide annotation text or --clear", err=True)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Section commands
# ---------------------------------------------------------------------------


def _cell_index(manifest, cell_id: str) -> int:
    """Return the index of a cell in the manifest's cell list."""
    for i, c in enumerate(manifest.cells):
        if c.id == cell_id:
            return i
    return -1


def _detect_overlaps(
    manifest, target_section_id: str | None, start_idx: int, end_idx: int
) -> list[OverlapAdjustment]:
    """Detect overlaps between [start_idx, end_idx] and existing sections.

    Returns a list of adjustments needed to resolve overlaps.
    The new section always takes priority.
    """
    cell_ids = [c.id for c in manifest.cells]
    cells = manifest.cells
    adjustments: list[OverlapAdjustment] = []

    for s in manifest.sections:
        if s.id == target_section_id:
            continue
        s_start = _cell_index(manifest, s.starts_at)
        if s_start == -1:
            continue
        if s.ends_at:
            s_end = _cell_index(manifest, s.ends_at)
            if s_end == -1:
                continue
        else:
            # Open-ended: find next section's start or end of notebook
            next_starts = sorted(
                _cell_index(manifest, other.starts_at)
                for other in manifest.sections
                if other.id != s.id and _cell_index(manifest, other.starts_at) > s_start
            )
            s_end = (next_starts[0] - 1) if next_starts else len(cell_ids) - 1

        # Check overlap: two ranges [a,b] and [c,d] overlap iff a <= d and c <= b
        if not (start_idx <= s_end and s_start <= end_idx):
            continue

        # Classify the overlap
        if s_start >= start_idx and s_end <= end_idx:
            # Existing entirely within new → remove
            adjustments.append(OverlapAdjustment(
                section_id=s.id,
                section_name=s.name,
                action=OverlapAction.REMOVE,
                description=f"Remove section '{s.name}' (entirely within new section)",
            ))
        elif s_start < start_idx:
            # Existing starts before new → trim its end
            new_end = cells[start_idx - 1].id
            new_end_name = cells[start_idx - 1].name
            adjustments.append(OverlapAdjustment(
                section_id=s.id,
                section_name=s.name,
                action=OverlapAction.TRIM_END,
                new_boundary=new_end,
                description=(
                    f"Trim section '{s.name}' end → "
                    f"cell {new_end[:8]} ({new_end_name})"
                ),
            ))
        elif s_end > end_idx:
            # Existing starts within new but extends beyond → trim its start
            new_start = cells[end_idx + 1].id
            new_start_name = cells[end_idx + 1].name
            adjustments.append(OverlapAdjustment(
                section_id=s.id,
                section_name=s.name,
                action=OverlapAction.TRIM_START,
                new_boundary=new_start,
                description=(
                    f"Trim section '{s.name}' start → "
                    f"cell {new_start[:8]} ({new_start_name})"
                ),
            ))

    return adjustments


def _format_overlap_prompt(adjustments: list[OverlapAdjustment]) -> str:
    """Format overlap adjustments into a human-readable message."""
    lines = ["Creating this section requires adjustments:"]
    for i, adj in enumerate(adjustments, 1):
        lines.append(f"  {i}. {adj.description}")
    return "\n".join(lines)


def _apply_overlap_adjustments(manifest, adjustments: list[OverlapAdjustment]) -> None:
    """Apply overlap adjustments to the manifest in place."""
    remove_ids: set[str] = set()
    for adj in adjustments:
        if adj.action == OverlapAction.TRIM_END:
            for s in manifest.sections:
                if s.id == adj.section_id:
                    s.ends_at = adj.new_boundary
                    break
        elif adj.action == OverlapAction.TRIM_START:
            for s in manifest.sections:
                if s.id == adj.section_id:
                    s.starts_at = adj.new_boundary
                    break
        elif adj.action == OverlapAction.REMOVE:
            remove_ids.add(adj.section_id)

    if remove_ids:
        manifest.sections = [s for s in manifest.sections if s.id not in remove_ids]


def _confirm_overlaps(
    adjustments: list[OverlapAdjustment], auto_confirm: bool
) -> bool:
    """Show overlap adjustments and return True if user confirms."""
    msg = _format_overlap_prompt(adjustments)
    click.echo(msg)
    if auto_confirm:
        click.echo("Auto-confirmed (--yes).")
        return True
    return click.confirm("Proceed?")


@cli.command("add-section")
@click.argument("name")
@click.option("--before", "before_cell_id", default=None, help="Cell ID where section starts")
@click.option("--ends-at", "ends_at_cell_id", default=None, help="Cell ID where section ends (inclusive)")
@click.option("--yes", "-y", "auto_confirm", is_flag=True, help="Auto-confirm overlap adjustments")
def add_section(
    name: str,
    before_cell_id: str | None,
    ends_at_cell_id: str | None,
    auto_confirm: bool,
) -> None:
    """Add or update a section divider.

    With --before: create a new section starting at that cell.
    With --ends-at only: update an existing section's end boundary.

    If the new section overlaps existing sections, you'll be prompted to
    confirm adjustments. Use --yes to auto-confirm.
    """
    from lembic.models.notebook import NotebookSection
    from lembic.services.file_manager import FileManager

    project_dir = Path.cwd()
    fm = FileManager(project_dir)
    manifest = fm.load_manifest()

    if not before_cell_id and not ends_at_cell_id:
        click.echo("Error: provide --before, --ends-at, or both.", err=True)
        sys.exit(1)

    # Resolve ends_at cell ID if provided
    ends_at_full_id: str | None = None
    if ends_at_cell_id:
        ends_at_full_id = fm.get_cell_entry(ends_at_cell_id).id

    if before_cell_id:
        # --- Create new section ---
        existing_section_names = {s.name for s in manifest.sections}
        if name in existing_section_names:
            click.echo(f"Error: a section named '{name}' already exists.", err=True)
            sys.exit(1)

        entry = fm.get_cell_entry(before_cell_id)
        start_idx = _cell_index(manifest, entry.id)

        if ends_at_full_id:
            end_idx = _cell_index(manifest, ends_at_full_id)
            if end_idx < start_idx:
                click.echo("Error: --ends-at cell must be at or after --before cell.", err=True)
                sys.exit(1)
        else:
            # Open-ended: effective end is next section start - 1, or last cell
            next_starts = sorted(
                _cell_index(manifest, s.starts_at)
                for s in manifest.sections
                if _cell_index(manifest, s.starts_at) > start_idx
            )
            end_idx = (next_starts[0] - 1) if next_starts else len(manifest.cells) - 1

        adjustments = _detect_overlaps(manifest, None, start_idx, end_idx)
        if adjustments:
            if not _confirm_overlaps(adjustments, auto_confirm):
                sys.exit(0)
            _apply_overlap_adjustments(manifest, adjustments)

        section = NotebookSection(
            id=fm._generate_unique_section_id(),
            name=name,
            starts_at=entry.id,
            ends_at=ends_at_full_id,
        )
        manifest.sections.append(section)
        fm.save_manifest()
        msg = f"Added section '{name}' (id={section.id}) before {entry.id}"
        if ends_at_full_id:
            msg += f", ends at {ends_at_full_id}"
        click.echo(msg)
    else:
        # --- Update existing section's ends_at ---
        assert ends_at_full_id is not None
        end_idx = _cell_index(manifest, ends_at_full_id)

        if name:
            # Find by name, ID, or prefix
            from lembic.errors import SectionNotFoundError
            try:
                target = fm.get_section_entry(name)
            except SectionNotFoundError:
                click.echo(f"Error: no section matching '{name}'.", err=True)
                sys.exit(1)
        else:
            # Empty name: find nearest preceding section
            target = None
            best_start = -1
            for s in manifest.sections:
                s_start = _cell_index(manifest, s.starts_at)
                if s_start != -1 and s_start <= end_idx and s_start > best_start:
                    best_start = s_start
                    target = s
            if target is None:
                click.echo("Error: no section found at or before that cell.", err=True)
                sys.exit(1)

        start_idx = _cell_index(manifest, target.starts_at)
        if end_idx < start_idx:
            click.echo("Error: --ends-at cell must be at or after section start.", err=True)
            sys.exit(1)

        adjustments = _detect_overlaps(manifest, target.id, start_idx, end_idx)
        if adjustments:
            if not _confirm_overlaps(adjustments, auto_confirm):
                sys.exit(0)
            _apply_overlap_adjustments(manifest, adjustments)

        target.ends_at = ends_at_full_id
        fm.save_manifest()
        click.echo(f"Updated section '{target.name}' ends_at → {ends_at_full_id}")


@cli.command("delete-section")
@click.argument("section_id")
def delete_section(section_id: str) -> None:
    """Remove a section divider (by ID, prefix, or name)."""
    from lembic.errors import SectionNotFoundError
    from lembic.services.file_manager import FileManager

    project_dir = Path.cwd()
    fm = FileManager(project_dir)
    manifest = fm.load_manifest()

    try:
        section = fm.get_section_entry(section_id)
    except SectionNotFoundError as e:
        click.echo(str(e), err=True)
        sys.exit(1)

    manifest.sections = [s for s in manifest.sections if s.id != section.id]
    fm.save_manifest()
    click.echo(f"Deleted section {section.id} ({section.name})")


@cli.command("clear-sections")
@click.option("--yes", "-y", "auto_confirm", is_flag=True, help="Skip confirmation prompt")
def clear_sections(auto_confirm: bool) -> None:
    """Remove all section dividers."""
    from lembic.services.file_manager import FileManager

    project_dir = Path.cwd()
    fm = FileManager(project_dir)
    manifest = fm.load_manifest()

    count = len(manifest.sections)
    if count == 0:
        click.echo("No sections to remove.")
        return

    if not auto_confirm:
        click.echo(f"This will remove all {count} section(s):")
        for s in manifest.sections:
            click.echo(f"  - {s.name} ({s.id})")
        if not click.confirm("Proceed?"):
            return

    manifest.sections = []
    fm.save_manifest()
    click.echo(f"Removed {count} section(s).")
