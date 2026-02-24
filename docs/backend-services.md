# Backend Services

All backend services live in `backend/dataflow/services/`. This document describes each service, its responsibilities, and key implementation details.

## FileManager

**File:** `services/file_manager.py`

The backbone of the system. Manages the YAML manifest and all cell files on disk.

### Responsibilities

- Load and save the `dataflow.yaml` manifest
- Cell CRUD: create, read, write, delete, rename, move, reorder
- Content hashing (SHA-256) for change detection
- Cell name generation using word pairs

### Key Implementation Details

- **Manifest caching**: The parsed manifest is cached in memory and invalidated on any write operation
- **YAML serialization**: CellType enums are manually converted to `.value` strings before YAML dump to avoid Python-specific tags
- **Cell file naming**: `{id}_{name}.py` (or `.md` for markdown cells)
- **Atomic operations**: Manifest is always written as a complete file (no partial updates)

### Methods

| Method | Description |
|--------|-------------|
| `load_manifest()` | Load and cache the YAML manifest |
| `save_manifest(manifest)` | Write manifest to disk, invalidate cache |
| `get_cell_entry(cell_id)` | Look up a cell in the manifest |
| `read_cell(cell_id)` | Read cell file content |
| `write_cell(cell_id, content)` | Write cell file content |
| `create_cell(type, name, content, after_id)` | Create cell, add to manifest, write file |
| `delete_cell(cell_id)` | Remove cell from manifest, delete file |
| `rename_cell(cell_id, new_name)` | Rename cell, rename file, update manifest |
| `move_cell(cell_id, after_id)` | Move cell after another in the manifest |
| `reorder_cells(cell_ids)` | Reorder all cells to match the given ID list |
| `cell_content_hash(cell_id)` | SHA-256 hash of cell content |

## KernelManager

**File:** `services/kernel_manager.py`

Wraps `jupyter_client.AsyncKernelManager` to provide a clean async interface for kernel operations.

### Responsibilities

- Start, restart, and shut down the Jupyter kernel
- Execute code and yield IOPub messages as an async generator
- Introspect kernel variables
- Inject startup code (sys.path, matplotlib inline, etc.)

### Startup Injection

When the kernel starts, the following code is executed silently:

```python
import sys
sys.path.insert(0, '<project_dir>')

# Configure matplotlib for inline rendering
try:
    import matplotlib
    matplotlib.use('Agg')
    %matplotlib inline
except ImportError:
    pass

# Suppress warnings in output
import warnings
warnings.filterwarnings('ignore')
```

### Methods

| Method | Description |
|--------|-------------|
| `start()` | Start the Jupyter kernel |
| `execute(code)` | Execute code, yield IOPub messages (async generator) |
| `interrupt()` | Send interrupt signal to kernel |
| `restart()` | Restart the kernel |
| `shutdown()` | Shut down the kernel |
| `get_variables()` | Introspect kernel namespace for variables |
| `is_started` | Property indicating whether kernel is running |

## CellExecutor

**File:** `services/cell_executor.py`

Orchestrates cell execution through the kernel with real-time WebSocket streaming.

### Key Design: Execution Lock

An `asyncio.Lock` ensures sequential execution. This is critical for "Run All" and "Run Range" operations where cells must execute in order, but WebSocket streaming must still be real-time.

### Post-Execution Pipeline

After each execution:
1. Log the event with AST-derived variable dependencies
2. Recompute cell states using the warning engine
3. Broadcast updated states to all WebSocket clients

## PtyManager

**File:** `services/pty_manager.py`

Manages a pseudo-terminal for the terminal pane.

### Implementation

- Creates a PTY using `pty.openpty()` + `os.fork()`
- The child process executes `/bin/bash` in the project directory
- File descriptor is set to non-blocking mode
- Async read uses `select()` with a 100ms timeout
- Resize is handled via `TIOCSWINSZ` ioctl

### Methods

| Method | Description |
|--------|-------------|
| `start(command, cwd)` | Fork a process with PTY |
| `read()` | Async read from PTY fd |
| `write(data)` | Write bytes to PTY fd |
| `resize(rows, cols)` | Send TIOCSWINSZ to PTY |
| `shutdown()` | Terminate the child process |

## ExecutionLog

**File:** `services/execution_log.py`

Thread-safe JSONL append-only log of execution events.

### Format

Each line is a JSON object:

```json
{
  "cell_id": "abc12345",
  "timestamp": "2024-01-01T12:00:00Z",
  "status": "ok",
  "duration_ms": 142.5,
  "variables_defined": ["df", "fig"],
  "variables_read": ["pd", "data"],
  "error": null
}
```

### Cell State Computation

The log is the source of truth for computing cell states:

| Condition | State |
|-----------|-------|
| No execution event | `idle` |
| Last event status = error | `error` |
| Content hash changed since last run | `stale` |
| Otherwise | `success` |

## WarningEngine

**File:** `services/warning_engine.py`

Computes cell states and generates warnings by combining execution history with AST-based dependency analysis.

### Stale Upstream Detection

For each cell, the engine checks if any variable it reads was redefined by another cell that ran after it:

```
Cell A defines x (ran at T=10)
Cell B reads x (ran at T=5)
→ Cell B is stale_upstream (its view of x is outdated)
```

### Out-of-Order Warnings

The engine also detects when cells with dependencies are executed out of order relative to their notebook position.

## AST Analyzer

**File:** `services/ast_analyzer.py`

Extracts variable dependencies from Python source code using the AST module.

### What It Extracts

- **Variables defined**: Assignments, function defs, class defs, for-loop targets, imports
- **Variables read**: Name references in load context, minus locally defined names
- **Imports**: Full module names (e.g., `pandas`, `numpy.linalg`)

### Import Cycle Detection

The `detect_import_cycles()` function builds a dependency graph from `lib/` Python files and uses DFS to detect circular imports.

## Profiler

**File:** `services/profiler.py`

Generates DataFrame profiling data by executing profiling code in the kernel.

### How It Works

1. `generate_profile_code(variable_name)` creates Python code that inspects a DataFrame
2. The code is executed in the kernel, producing JSON output
3. `parse_profile_result(output_text)` parses the JSON into a `DataProfile` model

### Profile Data

For each column: name, dtype, count, null count, unique count, top values, and numeric statistics (mean, std, min, max, median).

## OutputHandler

**File:** `services/output_handler.py`

Processes kernel outputs and persists them to disk.

### Plot Saving

PNG and SVG images from `display_data` messages are decoded and saved to `outputs/plots/` with the naming pattern: `{cell_id}_{timestamp}_{random}.{ext}`

### Table Saving

JSON table data is saved to `outputs/tables/`.

## VersionHistory

**File:** `services/version_history.py`

Manages per-cell version snapshots in `.dataflow/history/`.

### Storage Format

```
.dataflow/history/
└── {cell_id}/
    ├── 1706000000000.py        # Source snapshot
    ├── 1706000000000.meta.json # Metadata
    ├── 1706000500000.py
    └── 1706000500000.meta.json
```

Metadata includes cell_id, timestamp (ms), and file size. Old snapshots are pruned to keep the last 50 per cell.

## Exporter

**File:** `services/exporter.py`

Exports the notebook to various formats.

### Jupyter Notebook (.ipynb)

Creates a standard nbformat v4 notebook. Code and define cells become code cells, markdown cells stay as markdown. DataFlow metadata (cell ID and name) is preserved in cell metadata.

### Python Script (.py)

Creates a script with `# %%` cell markers (compatible with VS Code's Python extension). Markdown cells are commented out.

### Python Package

Creates a proper `src/` layout package with `pyproject.toml`. Each code cell becomes a module file.

## NameGenerator

**File:** `services/name_generator.py`

Generates human-readable cell names using adjective-noun word pairs (e.g., "mossy-stream", "focal-chain"). Contains ~200 adjectives and ~200 nouns for ~40,000 unique combinations. The generator accepts an `existing` set to avoid collisions.
