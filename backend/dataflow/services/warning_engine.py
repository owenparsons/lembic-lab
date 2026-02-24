"""Warning engine: computes cell states and stale/out-of-order warnings."""

from __future__ import annotations

from dataflow.models.cells import CellState
from dataflow.models.execution import ExecutionEvent, ExecutionStatus
from dataflow.models.notebook import NotebookManifest
from dataflow.services.ast_analyzer import analyze_cell
from dataflow.services.file_manager import FileManager


def compute_warnings(
    manifest: NotebookManifest,
    events: list[ExecutionEvent],
    file_manager: FileManager,
) -> tuple[dict[str, CellState], list[str]]:
    """Compute cell states and generate warnings.

    Returns (states, warnings) where:
    - states maps cell_id → CellState
    - warnings is a list of human-readable warning strings
    """
    states: dict[str, CellState] = {}
    warnings: list[str] = []
    cell_ids = [e.id for e in manifest.cells]
    cell_names = {e.id: e.name for e in manifest.cells}

    # Build last execution event per cell
    last_event: dict[str, ExecutionEvent] = {}
    for event in events:
        last_event[event.cell_id] = event

    # Build execution order (timestamps of last run)
    execution_order: dict[str, float] = {}
    for cid, event in last_event.items():
        execution_order[cid] = event.timestamp.timestamp()

    # Build variable producer map: variable_name → cell_id that last defined it
    var_producer: dict[str, str] = {}
    for event in events:
        for var in event.variables_defined:
            var_producer[var] = event.cell_id

    # Compute per-cell state
    for cell_entry in manifest.cells:
        cid = cell_entry.id
        event = last_event.get(cid)

        if event is None:
            states[cid] = CellState.IDLE
            continue

        if event.status == ExecutionStatus.ERROR:
            states[cid] = CellState.ERROR
            continue

        # Check if content has changed since last run (stale)
        try:
            current_hash = file_manager.cell_content_hash(cid)
            source = file_manager.read_cell(cid)
            deps = analyze_cell(source)
        except Exception:
            states[cid] = CellState.SUCCESS
            continue

        # Check if any upstream cell was re-run after this cell
        upstream_stale = False
        my_run_time = execution_order.get(cid, 0)
        for var in deps.variables_read:
            producer_id = var_producer.get(var)
            if producer_id and producer_id != cid:
                producer_run_time = execution_order.get(producer_id, 0)
                if producer_run_time > my_run_time:
                    upstream_stale = True
                    warnings.append(
                        f"'{cell_names.get(cid, cid)}' depends on '{var}' "
                        f"which was redefined by '{cell_names.get(producer_id, producer_id)}' "
                        f"after this cell last ran"
                    )

        if upstream_stale:
            states[cid] = CellState.STALE_UPSTREAM
        else:
            states[cid] = CellState.SUCCESS

    # Check for out-of-order execution
    for i, entry_a in enumerate(manifest.cells):
        for entry_b in manifest.cells[i + 1 :]:
            a_time = execution_order.get(entry_a.id)
            b_time = execution_order.get(entry_b.id)
            if a_time is not None and b_time is not None:
                if b_time < a_time:
                    # Cell B appears after A in notebook but ran before A
                    try:
                        source_a = file_manager.read_cell(entry_a.id)
                        deps_a = analyze_cell(source_a)
                        source_b = file_manager.read_cell(entry_b.id)
                        deps_b = analyze_cell(source_b)
                        # Only warn if there's an actual dependency
                        shared = deps_b.variables_read & deps_a.variables_defined
                        if shared:
                            warnings.append(
                                f"'{cell_names.get(entry_b.id, entry_b.id)}' "
                                f"reads {shared} defined by "
                                f"'{cell_names.get(entry_a.id, entry_a.id)}' "
                                f"but was run before it"
                            )
                    except Exception:
                        pass

    return states, warnings
