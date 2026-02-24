"""WebSocket message types for all three WS connections."""

from typing import Any, Literal

from pydantic import BaseModel, Field


# --- /ws/kernel messages (server → client) ---

class CellStatusMessage(BaseModel):
    type: Literal["cell_status"] = "cell_status"
    cell_id: str
    state: str


class StreamMessage(BaseModel):
    type: Literal["stream"] = "stream"
    cell_id: str
    stream: Literal["stdout", "stderr"]
    text: str


class DisplayDataMessage(BaseModel):
    type: Literal["display_data"] = "display_data"
    cell_id: str
    data: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExecuteResultMessage(BaseModel):
    type: Literal["execute_result"] = "execute_result"
    cell_id: str
    data: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)


class ErrorMessage(BaseModel):
    type: Literal["error"] = "error"
    cell_id: str
    ename: str
    evalue: str
    traceback: list[str] = Field(default_factory=list)


class ExecuteReplyMessage(BaseModel):
    type: Literal["execute_reply"] = "execute_reply"
    cell_id: str
    status: Literal["ok", "error"]
    duration_ms: float


class VariablesUpdateMessage(BaseModel):
    type: Literal["variables_update"] = "variables_update"
    variables: list[dict[str, Any]] = Field(default_factory=list)


class KernelStatusMessage(BaseModel):
    type: Literal["kernel_status"] = "kernel_status"
    status: str
    kernel_id: str | None = None


class CellStatesMessage(BaseModel):
    type: Literal["cell_states"] = "cell_states"
    states: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


KernelMessage = (
    CellStatusMessage
    | StreamMessage
    | DisplayDataMessage
    | ExecuteResultMessage
    | ErrorMessage
    | ExecuteReplyMessage
    | VariablesUpdateMessage
    | KernelStatusMessage
    | CellStatesMessage
)


# --- /ws/terminal messages ---

class TerminalResizeMessage(BaseModel):
    type: Literal["resize"] = "resize"
    cols: int
    rows: int


class TerminalInjectMessage(BaseModel):
    type: Literal["inject"] = "inject"
    message: str
    attachments: list[dict[str, str]] = Field(default_factory=list)


# --- /ws/filewatcher messages (server → client) ---

class CellModifiedMessage(BaseModel):
    type: Literal["cell_modified"] = "cell_modified"
    cell_id: str
    new_content: str
    new_hash: str


class ManifestModifiedMessage(BaseModel):
    type: Literal["manifest_modified"] = "manifest_modified"
    manifest: dict[str, Any]


class OutputAddedMessage(BaseModel):
    type: Literal["output_added"] = "output_added"
    output_type: str
    path: str
