# Execution Pipeline

This document describes the full lifecycle of a cell execution, from user click to output display.

## Overview

```
User clicks "Run"
    │
    ▼
Frontend: save if dirty → POST /api/run/{cell_id}
    │
    ▼
Backend: CellExecutor.execute_cell()
    │
    ├── Load cell source from FileManager
    ├── AST pre-analysis (variable dependencies)
    ├── Acquire execution lock
    │
    ▼
CellExecutor._run()
    │
    ├── Broadcast cell_status: running (via WS)
    ├── Submit code to KernelManager.execute()
    │
    ├── Async loop reading IOPub messages:
    │   ├── stream → broadcast via WS, collect
    │   ├── display_data → broadcast via WS, collect
    │   ├── execute_result → broadcast via WS, collect
    │   └── error → broadcast via WS, set ERROR status
    │
    ├── Broadcast execute_reply (status + duration)
    ├── Append ExecutionEvent to JSONL log
    ├── Recompute cell states + warnings
    └── Broadcast cell_states via WS
    │
    ▼
Frontend receives WS messages:
    ├── cell_status → update store, clear outputs if "running"
    ├── stream/display_data/execute_result → append to cell outputs
    ├── error → append to outputs, set error state
    ├── execute_reply → set final state (success/error)
    └── cell_states → update all cell states + warnings
```

## Detailed Steps

### 1. Frontend Initiates Execution

When the user clicks "Run" on a cell (or uses Shift+Enter):

```typescript
// CellList.tsx
const handleRunCell = async (cellId: string) => {
  if (dirty.has(cellId)) {
    await saveCell(cellId);  // Save unsaved changes first
  }
  await executionApi.runCell(cellId);
};
```

### 2. REST Request

`POST /api/run/{cell_id}` → `CellExecutor.execute_cell()`

The executor:
1. Loads the cell entry from the manifest
2. Reads the cell source from disk
3. Ensures the kernel is started (lazy init on first execution)
4. Acquires the execution lock (prevents concurrent execution)

### 3. AST Pre-Analysis

Before submitting code to the kernel, the AST analyzer extracts:

- **`variables_read`**: Variables referenced but not defined in this cell
- **`variables_defined`**: Variables assigned, including function/class definitions and imports
- **`imports`**: Module names imported

This information is stored in the execution log for dependency tracking.

### 4. Kernel Submission

The `KernelManager.execute()` method:

1. Calls `client.execute(source, reply=False)` on the Jupyter kernel
2. Returns an async generator that yields IOPub messages
3. Messages arrive as the kernel processes the code (stream output appears in real-time)
4. The generator terminates when an `execute_reply` message arrives

### 5. Output Collection

The executor iterates over kernel messages and handles each type:

| Kernel Message | Action |
|----------------|--------|
| `stream` | Broadcast to WS clients immediately |
| `display_data` | Broadcast to WS clients (includes base64 images, HTML, etc.) |
| `execute_result` | Broadcast to WS clients |
| `error` | Broadcast to WS clients, set status to ERROR |
| `execute_reply` | Signals completion |

Each message is also collected into the `outputs` list for the REST response.

### 6. Execution Lock

An `asyncio.Lock` ensures that when running multiple cells (via "Run All" or "Run Range"), they execute sequentially. WebSocket broadcasting happens inside the lock, so output streams in real-time even during sequential execution.

### 7. Post-Execution

After the kernel finishes:

1. **Execute reply** is broadcast with status (`"ok"` or `"error"`) and duration in milliseconds
2. **Execution event** is appended to the JSONL log with:
   - Cell ID, timestamp, status, duration
   - Variables defined and read (from AST analysis)
   - Error info (if applicable)
3. **Cell states** are recomputed by the warning engine and broadcast to all clients

### 8. Frontend State Updates

The `useKernelSocket` hook dispatches incoming WS messages to stores:

| WS Message | Store Update |
|------------|-------------|
| `cell_status: running` | Clear cell outputs, set running state |
| `stream` | Append to cell outputs |
| `display_data` | Append to cell outputs |
| `execute_result` | Append to cell outputs |
| `error` | Append to cell outputs, set error state |
| `execute_reply` | Set final state (success/error), clear running |
| `cell_states` | Update all cell states + warning indicators |

### 9. Output Rendering

The `OutputRenderer` component renders the collected outputs:

- **Stream** → `TextOutput` (ANSI-stripped monospace text)
- **Images** → `ImageOutput` (base64 PNG/SVG/JPEG)
- **HTML** → `HtmlOutput` (sandboxed iframe with dark theme, auto-sizing)
- **Tables** → `TableOutput` (when `application/json` contains an array)
- **Errors** → `ErrorOutput` (red background, formatted traceback)

## Warning Computation

After each execution, the warning engine runs:

1. **Build variable producer map**: For each variable, track which cell last defined it
2. **Check upstream staleness**: If cell B reads variable `x` defined by cell A, and cell A ran after cell B, then cell B is `stale_upstream`
3. **Check execution order**: If cell B appears after cell A in the notebook but ran before it, and B reads variables defined by A, generate an out-of-order warning

Warnings are displayed in the `WarningIndicator` component in the toolbar.

## Error Handling

- If the cell doesn't exist: HTTP 404
- If the kernel hasn't started and can't be started: HTTP 503
- If kernel execution fails: Error is captured and returned in the `ExecutionResult`
- If WebSocket broadcast fails: Silently ignored (client may have disconnected)
