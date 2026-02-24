# Frontend State Management

DataFlow uses [Zustand](https://zustand-demo.pmnd.rs/) for state management, with separate stores per domain. This keeps concerns isolated and makes it easy to subscribe to only the data a component needs.

## Store Overview

| Store | File | Persisted | Key Data |
|-------|------|-----------|----------|
| `notebookStore` | `stores/notebookStore.ts` | No | Cells, content, outputs, dirty tracking |
| `kernelStore` | `stores/kernelStore.ts` | No | Kernel status |
| `executionStore` | `stores/executionStore.ts` | No | Cell states, warnings, running cell |
| `terminalStore` | `stores/terminalStore.ts` | No | Connection state, injection |
| `uiStore` | `stores/uiStore.ts` | Yes | Layout, selection, mode, panel toggles |
| `variableStore` | `stores/variableStore.ts` | No | Kernel variables |
| `profileStore` | `stores/profileStore.ts` | No | DataFrame profiles |

## notebookStore

The central store for notebook data. Manages cells, their content, outputs, and dirty tracking.

### State

```typescript
interface NotebookState {
  cells: CellResponse[];        // Ordered list of cells
  contents: Record<string, string>;  // Local edits (cell_id → content)
  dirty: Set<string>;           // Cell IDs with unsaved changes
  loading: boolean;

  // Actions
  loadNotebook: () => Promise<void>;
  addCell: (data: CellCreate) => Promise<CellResponse | null>;
  deleteCell: (cellId: string) => Promise<void>;
  updateContent: (cellId: string, content: string) => void;
  saveCell: (cellId: string) => Promise<void>;
  saveAll: () => Promise<void>;
  setCellState: (cellId: string, state: CellState) => void;
  appendOutput: (cellId: string, output: CellOutput) => void;
  clearOutputs: (cellId: string) => void;
}
```

### Dirty Tracking

When a user edits a cell in the Monaco editor, `updateContent()` is called. This stores the new content in `contents` and adds the cell ID to `dirty`. When the cell is saved (via `saveCell()` or `saveAll()`), the content is sent to the backend and the cell is removed from `dirty`.

### Output Management

Cell outputs are stored on the `CellResponse` objects in the `cells` array. When a cell starts running, `clearOutputs()` empties the array. As execution streams messages, `appendOutput()` adds each output.

## kernelStore

Tracks the kernel lifecycle status.

```typescript
interface KernelState {
  status: "idle" | "busy" | "disconnected" | "starting" | "error";
  setStatus: (status: string) => void;
}
```

## executionStore

Tracks execution state across all cells.

```typescript
interface ExecutionState {
  cellStates: Record<string, CellState>;  // Per-cell execution state
  logEntries: ExecutionEvent[];            // Execution history
  warnings: string[];                      // Active warnings
  runningCellId: string | null;            // Currently executing cell
  runningStartTime: number | null;         // For elapsed time display

  setCellStates: (states: Record<string, CellState>) => void;
  setCellState: (cellId: string, state: CellState) => void;
  setWarnings: (warnings: string[]) => void;
  addLogEntry: (entry: ExecutionEvent) => void;
  setRunning: (cellId: string | null) => void;
}
```

### Cell State Flow

```
idle → running → success
                → error
                → stale (if content changes after success)
                → stale_upstream (if dependency changes)
```

## uiStore

UI preferences and interaction state. Persisted to localStorage via `zustand/persist`.

```typescript
interface UiState {
  paneOrder: "notebook-terminal" | "terminal-notebook";
  notebookPaneSize: number;              // Percentage
  selectedCellId: string | null;
  mode: "command" | "edit";
  variableExplorerOpen: boolean;
  profilePanelOpen: boolean;
  dependencyGraphOpen: boolean;

  togglePaneOrder: () => void;
  setPaneSize: (size: number) => void;
  selectCell: (cellId: string | null) => void;
  setMode: (mode: Mode) => void;
  toggleVariableExplorer: () => void;
  toggleProfilePanel: () => void;
  toggleDependencyGraph: () => void;
}
```

### Persistence

Only layout preferences are persisted:
- `paneOrder`
- `notebookPaneSize`
- `variableExplorerOpen`

Selection and mode reset on page load.

## variableStore

Kernel variable introspection data.

```typescript
interface VariableState {
  variables: VariableInfo[];  // { name, var_type, shape?, size_bytes?, preview }
  loading: boolean;
  refresh: () => Promise<void>;
}
```

The Variable Explorer calls `refresh()` on mount and after each execution.

## profileStore

DataFrame profiling results.

```typescript
interface ProfileState {
  profiles: Record<string, DataProfile>;  // variable_name → profile
  loading: boolean;
  loadProfile: (variableName: string) => Promise<void>;
}
```

Profiles are loaded on demand when the user clicks a DataFrame in the Variable Explorer.

## Store Interaction Patterns

### WebSocket → Store Updates

The `useKernelSocket` hook receives WebSocket messages and dispatches to multiple stores:

```
WS: cell_status    → notebookStore.setCellState + executionStore.setCellState
WS: stream         → notebookStore.appendOutput
WS: execute_reply  → notebookStore.setCellState + executionStore.setRunning(null)
WS: cell_states    → executionStore.setCellStates + executionStore.setWarnings
WS: kernel_status  → kernelStore.setStatus
```

### Cross-Store Access

Stores can access each other via `getState()`:

```typescript
// In useKeyboardShortcuts hook
const store = useNotebookStore.getState();
if (store.dirty.has(selectedCellId)) {
  await store.saveCell(selectedCellId);
}
```

This is used in keyboard shortcuts and other imperative code where hook-based subscriptions aren't appropriate.
