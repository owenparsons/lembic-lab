# Architecture

## Overview

DataFlow is a monorepo with two packages: a FastAPI backend and a React frontend. The two communicate via REST API for commands and WebSockets for real-time streaming.

```
┌─────────────────────────────────────────────────────────┐
│  Browser (React + Vite)                                 │
│                                                         │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Notebook    │  │  Terminal    │  │  Side Panels │   │
│  │  Pane        │  │  Pane       │  │  (Var/Prof/  │   │
│  │             │  │  (xterm.js) │  │   DAG)       │   │
│  └──────┬──────┘  └──────┬──────┘  └──────┬───────┘   │
│         │                │                │            │
│    REST API         WS /terminal     REST API          │
│    WS /kernel       (binary)         WS /filewatcher   │
└─────────┼────────────────┼────────────────┼────────────┘
          │                │                │
┌─────────┼────────────────┼────────────────┼────────────┐
│  FastAPI Backend (uvicorn)                              │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Cell         │  │ PTY          │  │ File         │  │
│  │ Executor     │  │ Manager      │  │ Watcher      │  │
│  └──────┬───────┘  └──────────────┘  └──────────────┘  │
│         │                                               │
│  ┌──────┴───────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Kernel       │  │ File         │  │ Execution    │  │
│  │ Manager      │  │ Manager      │  │ Log          │  │
│  │ (Jupyter)    │  │ (YAML/Files) │  │ (JSONL)      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
          │                │
          ▼                ▼
    IPython Kernel    Project Directory
                      (cells/, lib/, outputs/)
```

## Backend Architecture

### Application Lifecycle

The FastAPI app uses a factory pattern (`create_app()`) with a lifespan context manager. On startup:

1. `AppState` is created with the project directory path
2. Core services are initialized: `FileManager`, `ExecutionLog`, `ConnectionManager`
3. Heavy services are left for lazy initialization: `KernelManager`, `PtyManager`, `CellExecutor`

On shutdown:
1. Kernel is shut down (if started)
2. PTY process is terminated (if started)

### Service Layer

Services are injected via FastAPI's `Depends()` system. The dependency injection helpers live in `server/dependencies.py`.

**FileManager** — The backbone of the system. Manages the YAML manifest and all cell files on disk. All cell CRUD goes through this service. It caches the parsed manifest in memory and invalidates on write.

**KernelManager** — Wraps `jupyter_client.AsyncKernelManager`. Provides `execute()` as an async generator that yields IOPub messages. Also handles variable introspection via kernel code execution.

**CellExecutor** — Orchestrates execution. Holds an `asyncio.Lock` to ensure sequential execution during "run all" while keeping WebSocket streaming fully async. Flow:

1. Load cell source from FileManager
2. AST pre-analysis for variable dependencies
3. Broadcast `cell_status: running` via WS
4. Submit code to kernel, iterate IOPub messages
5. Broadcast each output (stream, display_data, execute_result, error) via WS
6. Broadcast `execute_reply` with duration
7. Append to execution log with dependency info
8. Recompute cell states and broadcast warnings

**PtyManager** — Manages a pseudo-terminal via `pty.openpty()` + `os.fork()`. Provides async read/write and resize. The terminal WebSocket endpoint bridges xterm.js to this PTY.

**ExecutionLog** — Thread-safe JSONL append-only log. Each execution event records: cell_id, timestamp, status, duration, variables_defined, variables_read. Used to compute cell states.

**WarningEngine** — Computes cell staleness and execution order warnings by combining the execution log with AST-based variable dependency analysis.

### WebSocket Connections

Three separate WebSocket connections serve distinct purposes:

| Endpoint | Format | Direction | Purpose |
|----------|--------|-----------|---------|
| `/ws/kernel` | JSON | Server → Client | Execution output streaming, cell state updates |
| `/ws/terminal` | Binary + JSON | Bidirectional | Terminal I/O (raw bytes) + control messages (resize, inject) |
| `/ws/filewatcher` | JSON | Server → Client | File change notifications |

The `ConnectionManager` maintains separate client lists for kernel and filewatcher connections and provides broadcast methods.

### File System Layout

A DataFlow project has a specific directory structure:

```
project/
├── dataflow.yaml           # Manifest: cell order + metadata
├── execution_log.jsonl     # Execution history
├── cells/                  # One file per cell
│   ├── abc12345_load-data.py
│   ├── def67890_analyze.py
│   └── ghi11111_notes.md
├── lib/                    # Reusable functions
│   ├── __init__.py
│   └── helpers.py
├── outputs/
│   ├── plots/              # Saved plot images
│   └── tables/             # Saved table JSON
├── .dataflow/
│   └── history/            # Per-cell version snapshots
│       ├── abc12345/
│       └── def67890/
├── CLAUDE.md               # Context file for CC
└── .gitignore
```

The manifest (`dataflow.yaml`) is the authoritative source for cell order:

```yaml
cells:
  - id: abc12345
    name: load-data
    type: code
    file: cells/abc12345_load-data.py
  - id: def67890
    name: analyze
    type: code
    file: cells/def67890_analyze.py
```

## Frontend Architecture

### State Management

The frontend uses Zustand with separate stores per domain:

| Store | Responsibility |
|-------|---------------|
| `notebookStore` | Cells, content, outputs, dirty tracking, CRUD operations |
| `kernelStore` | Kernel status (idle/busy/disconnected) |
| `executionStore` | Cell states, execution log, running cell, warnings |
| `terminalStore` | Terminal connection state, injection bar |
| `uiStore` | Layout preferences, selection, mode (persisted to localStorage) |
| `variableStore` | Kernel variable list |
| `profileStore` | DataFrame profiling results |

### Component Hierarchy

```
App
├── useKernelSocket (WebSocket hook)
├── useFileWatcherSocket (WebSocket hook)
├── useKeyboardShortcuts (keyboard handler)
└── AppShell
    ├── PanelGroup (resizable)
    │   ├── NotebookPane
    │   │   ├── Toolbar
    │   │   │   ├── ExecutionControls
    │   │   │   ├── CellOperations
    │   │   │   ├── UtilityButtons
    │   │   │   └── WarningIndicator
    │   │   └── CellList
    │   │       ├── AddCellButton
    │   │       ├── CodeCell
    │   │       │   ├── CellHeader
    │   │       │   ├── MonacoWrapper / <pre> (based on mode)
    │   │       │   └── OutputRenderer
    │   │       ├── MarkdownCell
    │   │       └── DefineCell
    │   ├── PaneHandle (resize + swap)
    │   └── TerminalPane
    │       ├── TerminalHeader
    │       ├── XTerminal
    │       └── InjectionBar
    ├── VariableExplorer (side panel)
    ├── DataProfilePanel (side panel)
    ├── DependencyGraph (side panel)
    └── StatusBar
```

### Dual Mode System

The UI operates in two modes, matching Jupyter's model:

- **Command mode**: Keyboard shortcuts navigate between cells and trigger actions. The editor is not focused.
- **Edit mode**: Keyboard input goes to the Monaco editor. Only Escape and execution shortcuts are active.

The mode is stored in `uiStore` and drives which keyboard shortcuts are active.

### Output Rendering Pipeline

Cell outputs are dispatched by type through `OutputRenderer`:

1. `stream` → `TextOutput` (strips ANSI codes)
2. `display_data` / `execute_result` → `RichOutput` which selects by MIME type:
   - `image/*` → `ImageOutput` (base64 `<img>` or inline SVG)
   - `text/html` → `HtmlOutput` (sandboxed iframe with dark theme)
   - `application/json` (array) → `TableOutput` (scrollable with sticky headers)
   - `text/plain` → `TextOutput`
3. `error` → `ErrorOutput` (formatted traceback with ANSI stripping)
