# WebSocket Protocol

DataFlow uses three separate WebSocket connections, each serving a distinct purpose.

## /ws/kernel

**Format:** JSON
**Direction:** Server → Client

Streams kernel execution messages and state updates to connected frontends. The `ConnectionManager` maintains a list of connected clients and broadcasts to all of them.

### Message Types

All messages are discriminated on the `type` field.

#### `cell_status`

Sent when a cell starts or finishes execution.

```json
{
  "type": "cell_status",
  "cell_id": "abc12345",
  "state": "running"
}
```

States: `"running"`, `"idle"`

#### `stream`

Standard output/error from code execution. Sent in real-time as the kernel produces output.

```json
{
  "type": "stream",
  "cell_id": "abc12345",
  "stream": "stdout",
  "text": "Hello, world!\n"
}
```

#### `display_data`

Rich output (plots, HTML, etc.) from `IPython.display` or matplotlib.

```json
{
  "type": "display_data",
  "cell_id": "abc12345",
  "data": {
    "image/png": "<base64-encoded-png>",
    "text/plain": "<Figure size 640x480>"
  },
  "metadata": {}
}
```

#### `execute_result`

The return value of the last expression in a cell.

```json
{
  "type": "execute_result",
  "cell_id": "abc12345",
  "data": {
    "text/plain": "42"
  },
  "metadata": {}
}
```

#### `error`

Execution error with traceback.

```json
{
  "type": "error",
  "cell_id": "abc12345",
  "ename": "NameError",
  "evalue": "name 'x' is not defined",
  "traceback": [
    "\u001b[0;31m---------------------------------------------------------------------------\u001b[0m",
    "\u001b[0;31mNameError\u001b[0m: name 'x' is not defined"
  ]
}
```

#### `execute_reply`

Sent after execution completes, with final status and timing.

```json
{
  "type": "execute_reply",
  "cell_id": "abc12345",
  "status": "ok",
  "duration_ms": 142.5
}
```

Status: `"ok"` or `"error"`

#### `cell_states`

Broadcast after each execution with recomputed cell states and warnings.

```json
{
  "type": "cell_states",
  "states": {
    "abc12345": "success",
    "def67890": "stale_upstream"
  },
  "warnings": [
    "'analyze' depends on 'df' which was redefined by 'load-data' after this cell last ran"
  ]
}
```

#### `kernel_status`

Kernel lifecycle events.

```json
{
  "type": "kernel_status",
  "status": "idle",
  "kernel_id": "uuid-string"
}
```

#### `variables_update`

Sent after execution with updated variable information.

```json
{
  "type": "variables_update",
  "variables": [
    {"name": "df", "var_type": "DataFrame", "shape": "(100, 5)", "size_bytes": 4200}
  ]
}
```

## /ws/terminal

**Format:** Binary (data) + JSON (control)
**Direction:** Bidirectional

Raw byte stream between xterm.js and the backend PTY. Also accepts JSON control messages.

### Data Messages

- **Client → Server:** Raw bytes from xterm.js (keyboard input)
- **Server → Client:** Raw bytes from PTY (terminal output), sent as `ArrayBuffer`

### Control Messages (Client → Server)

#### `resize`

Sent when the terminal container is resized.

```json
{
  "type": "resize",
  "cols": 120,
  "rows": 40
}
```

#### `inject`

Sent from the injection bar to write a message to the PTY stdin.

```json
{
  "type": "inject",
  "message": "Please analyze the data in cells/abc12345_load-data.py",
  "attachments": [
    {"type": "cell", "id": "abc12345", "name": "load-data"}
  ]
}
```

### Protocol Notes

- The WebSocket `binaryType` is set to `"arraybuffer"` on the client
- Text data from the client is UTF-8 encoded before sending
- The backend distinguishes binary (PTY data) from text (JSON control) messages
- On connection, the client sends an initial `resize` message with the terminal dimensions

## /ws/filewatcher

**Format:** JSON
**Direction:** Server → Client

Notifies the frontend when files are modified externally (e.g., by CC or another editor).

### Message Types

#### `cell_modified`

A cell file was changed on disk.

```json
{
  "type": "cell_modified",
  "cell_id": "abc12345",
  "new_content": "import pandas as pd\ndf = pd.read_csv('data.csv')",
  "new_hash": "sha256-hex-string"
}
```

The frontend checks if the cell is "dirty" (has unsaved local edits). If dirty, it flags a conflict for later resolution. If clean, it updates the cell content directly.

#### `manifest_modified`

The `dataflow.yaml` manifest was changed on disk.

```json
{
  "type": "manifest_modified",
  "manifest": {
    "cells": [...]
  }
}
```

#### `output_added`

A new output file was created (plot or table).

```json
{
  "type": "output_added",
  "output_type": "plot",
  "path": "outputs/plots/abc12345_1706000000_a1b2c3.png"
}
```

### File Watcher Implementation

The backend uses `watchdog` with:

- **300ms debounce** per file path (prevents event storms)
- **Content hashing** to suppress false positives (save without change)
- **Path filtering**: ignores `__pycache__/`, `*.pyc`, `.DS_Store`, `.dataflow/history/`, `execution_log.jsonl`, `.git`, `node_modules`
