# Build Log

This document describes how DataFlow was built, the phases of implementation, and notable decisions and fixes encountered along the way.

## Implementation Phases

The project was built incrementally across 6 phases, with each phase committed separately.

### Phase 0: Scaffolding

**Commits:** Phase 0.1-0.2, Phase 0.3-0.4, Phase 0.5

Set up the monorepo structure:
- Root `package.json` with npm workspaces
- Backend Python package with `pyproject.toml` (FastAPI, uvicorn, jupyter_client, pydantic, etc.)
- Frontend with Vite + React 18 + TypeScript
- Tailwind CSS with full dark theme design system (CSS custom properties)
- Dev startup script (`scripts/dev.sh`) running both servers concurrently

**Package manager choice:** `uv` was chosen for the Python backend over pip for speed and reliability.

### Phase 1A: Backend Foundation

**Commit:** Phase 1A: Complete backend foundation

Built the entire backend service layer:
- All Pydantic models (cells, notebook, execution, project, variables, profile, export, WS messages)
- FastAPI app factory with lifespan context manager
- AppState with dependency injection
- FileManager with full CRUD and manifest management
- Name generator (~200 adjectives x ~200 nouns)
- ExecutionLog (thread-safe JSONL)
- KernelManager (jupyter_client wrapper)
- PtyManager (PTY via openpty + fork)
- CellExecutor (execution orchestration)
- REST routers (cells, notebook, execution, project)
- WebSocket endpoints (kernel, terminal, filewatcher)
- ConnectionManager for WS broadcast
- CLI (click): `dataflow init`, `dataflow open`, `dataflow run-cell`
- Project scaffolding with CLAUDE.md generation
- 33 unit tests

### Phase 1B: Frontend Foundation

**Commits:** Phase 1B (1.9-1.12), Phase 1B (1.13-1.15), Phase 1B (1.16-1.17)

Built the frontend in three stages:

1. **Types, API, stores, shared components**: TypeScript types mirroring backend models, REST API client with typed fetch wrappers, Zustand stores, IconButton/Tooltip/Spinner/Badge/Modal/ContextMenu
2. **Layout and terminal**: AppShell with resizable split panes (react-resizable-panels), toolbar, xterm.js terminal with WebGL addon
3. **Cell rendering**: Monaco editor wrapper with auto-height and custom dark theme, CodeCell/MarkdownCell/CellHeader/CellOutput, useKernelSocket hook

### Phase 1.18-1.20: Wire Execution End-to-End

**Commit:** Phase 1.18-1.20

Connected all the pieces:
- Lazy CellExecutor + KernelManager initialization via dependency injection
- Variables endpoint
- Filewatcher WebSocket endpoint
- CLI tested: `dataflow init` creates proper project structure
- First working demo: edit code, run it, see output

### Phase 1C + 2: File Watching + Function Library + CC Integration

**Commit:** Phase 1C + 2

- File watcher (watchdog) with DebouncedHandler and content hashing
- AST analyzer for variable dependencies and import cycle detection
- useFileWatcherSocket hook
- DefineCell component (collapsed function display)
- InjectionBar + AttachmentChip for CC terminal integration

### Phase 3: Rich Outputs + Data Awareness

**Commit:** Phase 3

- Modular output renderers (TextOutput, ImageOutput, HtmlOutput, TableOutput, ErrorOutput)
- OutputRenderer dispatcher replacing monolithic CellOutput
- Backend output handler (saves plots/tables to disk)
- Backend data profiler (generates kernel profiling code)
- Profile API endpoint
- Variable Explorer panel (auto-refresh, DataFrame click-to-profile)
- Data Profile Panel with ProfileCard (per-column stats, top values, sample rows)

### Phase 4: Warnings, Navigation, Dependency Graph, Version History

**Commit:** Phase 4

- Warning engine (stale/stale_upstream detection, out-of-order warnings)
- Cell executor enhanced with AST dependency tracking and state broadcasts
- Dependency graph panel (SVG DAG with state-colored nodes)
- Version history service (per-cell snapshots in .dataflow/history/)
- History and cell states API endpoints

### Phase 5-6: Export, Keyboard Shortcuts, Polish

**Commit:** Phase 5-6

- Exporter: .ipynb, .py script (# %% markers), Python package (src/ layout)
- Full keyboard shortcut system (Jupyter-compatible command/edit mode)
- Conflict resolution dialog (side-by-side diff view)
- Export API endpoint

## Notable Fixes and Decisions

### YAML Enum Serialization

**Problem:** `yaml.dump` serialized CellType enum values as `!!python/object/apply:dataflow.models.cells.CellType` tags, which `yaml.safe_load` couldn't parse.

**Fix:** Manually convert enum values to `.value` strings in `save_manifest()` before YAML dump.

### WebSocket Dependency Injection

**Problem:** WebSocket endpoints can't use FastAPI's `Depends()` the same way as regular HTTP endpoints because `WebSocket` is not a `Request`.

**Fix:** Access state directly via `websocket.app.state.app_state` in WS handlers.

### react-resizable-panels v4 API Change

**Problem:** The library renamed its exports in v4: `PanelGroup` → `Group`, `PanelResizeHandle` → `Separator`, `direction` → `orientation`.

**Fix:** Updated all imports and props to match v4 API.

### Lucide Icon Types

**Problem:** Lucide icons are `ForwardRefExoticComponent`, not `React.FC`, causing type errors in the CellStateIcon ICON_MAP.

**Fix:** Typed the map as `Record<string, LucideIcon>` using the proper lucide type.

### AST Analyzer Import Tracking

**Problem:** `import pandas as pd` stored the alias "pd" in the imports set instead of the module name "pandas".

**Fix:** Store `alias.name` (full module name) in `imports` while keeping the alias in `defined`.

### NotebookManifest Name

**Problem:** The exporter assumed `NotebookManifest` had a `name` field, but it only has `cells`.

**Fix:** Derive the project name from the project directory name instead.

## Test Coverage

The final test suite includes 55 backend tests across 7 test files:

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `test_ast_analyzer.py` | 9 | Variable extraction, imports, functions, syntax errors, tuple unpacking |
| `test_execution_log.py` | 9 | Append/read, cell filtering, state computation, clear |
| `test_exporter.py` | 3 | Export to .ipynb, .py, package |
| `test_file_manager.py` | 13 | Full CRUD, ordering, move, rename, hash, reorder |
| `test_models.py` | 9 | Serialization/deserialization of all Pydantic models |
| `test_name_generator.py` | 3 | Uniqueness, collision avoidance |
| `test_version_history.py` | 5 | Save, list, get, nonexistent, separate histories |
| `test_warning_engine.py` | 5 | Idle, success, error, stale upstream, correct order |

Frontend TypeScript compiles cleanly with strict mode via `tsc --noEmit`.

## Commit History

```
114783e Phase 5-6: Export, keyboard shortcuts, conflict resolution
9fcf37e Phase 4: Warnings, dependency graph, version history
2b93765 Phase 3: Rich outputs, data profiler, variable explorer
d84f555 Phase 1C + 2: File watching, function library, CC integration
ba67ee1 Phase 1.18-1.20: Wire execution end-to-end, CLI, variables endpoint
ae41bf8 Phase 1B (1.16-1.17): Kernel WebSocket + notebook pane with cell rendering
964a9cc Phase 1B (1.13-1.15): AppShell with split panes, toolbar, terminal
46b3412 Phase 1B (1.9-1.12): Frontend types, API client, stores, shared components
c89722e Phase 1A: Complete backend foundation
d04138c Phase 0.5: Add dev startup script
83b8d46 Phase 0.3-0.4: Frontend with Vite, React, TypeScript, Tailwind dark theme
197678c Phase 0.1-0.2: Project scaffolding and backend package
```
