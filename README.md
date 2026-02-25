# Lembic Lab

A browser-based data science notebook environment designed for use with Claude Code. Named after the *alembic* — the vessel medieval alchemists used for distillation — Lembic transforms raw data into refined insight. The project structure (file-per-cell, manifest-driven, `lib/` function library) is optimised for CC to read, write, and navigate. The notebook provides the visual feedback loop (plots, tables, profiles) and the terminal pane gives CC direct access.

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- [uv](https://docs.astral.sh/uv/) (Python package manager)

### Installation

```bash
# Clone the repo
git clone <repo-url> && cd notebook_agent

# Install backend
cd backend && uv venv && uv pip install -e ".[dev]"

# Install frontend
cd ../frontend && npm install
```

### Usage

**Create a new project:**

```bash
lembic init my-analysis
cd my-analysis
```

This scaffolds a lembic notebook:

```
my-analysis/
├── cells/              # One file per cell
├── lib/                # Reusable function library
│   └── __init__.py
├── outputs/
│   ├── plots/
│   └── tables/
├── .notebook/
│   └── history/        # Version history
├── notebook.yaml       # Manifest (cell order + metadata)
├── CLAUDE.md           # Context file for CC
└── .gitignore
```

**Start the notebook:**

```bash
lembic open
```

This starts the backend (port 8000) and opens your browser. To start without opening a browser:

```bash
lembic open --no-browser --port 8001
```

**Run a cell headlessly (for CC autonomous iteration):**

```bash
lembic run-cell <cell_id>
```

### Development

To work on Lembic itself, start both servers from the repo root:

```bash
npm run dev
```

This runs the backend (uvicorn with hot-reload on :8000) and frontend (Vite on :5173) concurrently. Vite proxies `/api/*` and `/ws/*` to the backend.

**Run backend tests:**

```bash
cd backend && uv run python -m pytest tests/ -v
```

**TypeScript type checking:**

```bash
cd frontend && npm run typecheck
```

## Architecture

Lembic is a monorepo with two packages:

- **`backend/`** — FastAPI + Python: kernel management, cell execution, file I/O, WebSocket streaming
- **`frontend/`** — React 18 + Vite + TypeScript: notebook UI, Monaco editor, xterm.js terminal

### How It Works

1. Each notebook cell is a file on disk (`cells/{id}_{name}.py`)
2. A YAML manifest (`notebook.yaml`) defines cell order and metadata
3. The backend manages a Jupyter kernel for code execution
4. Execution outputs stream to the frontend via WebSocket in real-time
5. A file watcher detects external changes (e.g., CC editing files) and syncs the UI
6. The terminal pane provides direct PTY access for CC

### Key Design Decisions

- **File-per-cell**: Every cell is a standalone `.py` or `.md` file. CC can read and edit them directly.
- **Manifest-driven**: `notebook.yaml` is the source of truth for cell order and metadata.
- **Lazy kernel**: The Jupyter kernel only starts on first execution, keeping startup instant.
- **WebSocket streaming**: Execution output is streamed in real-time, not buffered.
- **Dark-mode-first**: The entire UI is designed around a dark color palette with CSS custom properties.

## Features

### Notebook

- Code cells with Monaco editor (Python syntax, auto-height, keybindings)
- Markdown cells with rendered preview and edit toggle
- Define cells for the `lib/` function library (collapsed by default)
- Add cells between existing cells with the inline "+" button
- Cell execution state tracking (idle, running, success, error, stale)

### Terminal

- Full terminal emulator via xterm.js with WebGL rendering
- Injection bar for sending messages/context to CC
- Attachment chips for including cell content in messages

### Output Rendering

- Text output with ANSI stripping
- Image output (PNG, SVG, JPEG) with lazy loading
- HTML output in sandboxed iframes (Plotly, Altair)
- Table output with sticky headers, row/column counts, and truncation
- Error output with formatted tracebacks

### Data Awareness

- Variable Explorer: lists kernel variables with type, shape, size, preview
- Data Profiler: per-column statistics, null counts, top values, sample rows
- Click any DataFrame in the Variable Explorer to profile it

### Dependency Tracking

- AST-based variable dependency extraction
- Stale cell detection (content changed since last run)
- Upstream stale detection (dependency redefined after this cell ran)
- Out-of-order execution warnings
- Visual dependency graph (SVG DAG)

### Version History

- Per-cell snapshots saved automatically on each edit
- Browse and restore previous versions via API

### Export

- **Jupyter Notebook** (`.ipynb`): standard format, opens in Jupyter
- **Python Script** (`.py`): with `# %%` cell markers for VS Code
- **Python Package**: proper `src/` layout with `pyproject.toml`

### Keyboard Shortcuts

Jupyter-compatible dual mode system:

| Shortcut | Mode | Action |
|----------|------|--------|
| `Enter` | Command | Enter edit mode |
| `Escape` | Edit | Exit to command mode |
| `Shift+Enter` | Command | Run cell |
| `Cmd+Enter` | Command | Run cell and advance |
| `Cmd+S` | Any | Save all |
| `j` / `Down` | Command | Select next cell |
| `k` / `Up` | Command | Select previous cell |
| `b` | Command | Add cell below |
| `a` | Command | Add cell above |
| `dd` | Command | Delete cell (press twice) |
| `ii` | Command | Interrupt kernel (press twice) |
| `00` | Command | Restart kernel (press twice) |

## API Reference

### REST Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/project` | Project info |
| `GET` | `/api/notebook` | Load full notebook |
| `POST` | `/api/notebook/save` | Save manifest |
| `GET` | `/api/cells` | List all cells |
| `POST` | `/api/cells` | Create cell |
| `GET` | `/api/cells/{id}` | Get cell |
| `PUT` | `/api/cells/{id}` | Update cell |
| `DELETE` | `/api/cells/{id}` | Delete cell |
| `POST` | `/api/cells/{id}/move` | Move cell |
| `GET` | `/api/cells/{id}/history` | Cell version history |
| `POST` | `/api/run/{cell_id}` | Run single cell |
| `POST` | `/api/run/range` | Run cell range |
| `POST` | `/api/run/all` | Run all cells |
| `GET` | `/api/cell-states` | Get states + warnings |
| `POST` | `/api/kernel/interrupt` | Interrupt kernel |
| `POST` | `/api/kernel/restart` | Restart kernel |
| `GET` | `/api/variables` | List kernel variables |
| `POST` | `/api/profile` | Profile a DataFrame |
| `POST` | `/api/export` | Export notebook |

### WebSocket Endpoints

| Path | Type | Description |
|------|------|-------------|
| `/ws/kernel` | JSON | Kernel execution messages |
| `/ws/terminal` | Binary + JSON | Terminal I/O |
| `/ws/filewatcher` | JSON | File change notifications |

## Tech Stack

### Backend

- [FastAPI](https://fastapi.tiangolo.com/) — async web framework
- [Pydantic v2](https://docs.pydantic.dev/) — data validation and serialization
- [jupyter_client](https://jupyter-client.readthedocs.io/) — Jupyter kernel management
- [watchdog](https://python-watchdog.readthedocs.io/) — file system monitoring
- [Click](https://click.palletsprojects.com/) — CLI framework
- [PyYAML](https://pyyaml.org/) — YAML parsing for manifests

### Frontend

- [React 18](https://react.dev/) — UI framework
- [TypeScript](https://www.typescriptlang.org/) — type safety
- [Vite](https://vitejs.dev/) — build tool and dev server
- [Tailwind CSS](https://tailwindcss.com/) — utility-first styling
- [Zustand](https://zustand-demo.pmnd.rs/) — state management
- [Monaco Editor](https://microsoft.github.io/monaco-editor/) — code editing
- [xterm.js](https://xtermjs.org/) — terminal emulator
- [react-resizable-panels](https://github.com/bvaughn/react-resizable-panels) — resizable pane layout
- [Lucide](https://lucide.dev/) — icon library
