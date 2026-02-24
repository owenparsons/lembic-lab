/**
 * Discriminated union for all WebSocket messages from /ws/kernel.
 */

export interface CellStatusMessage {
  type: "cell_status";
  cell_id: string;
  state: string;
}

export interface StreamMessage {
  type: "stream";
  cell_id: string;
  stream: "stdout" | "stderr";
  text: string;
}

export interface DisplayDataMessage {
  type: "display_data";
  cell_id: string;
  data: Record<string, unknown>;
  metadata: Record<string, unknown>;
}

export interface ExecuteResultMessage {
  type: "execute_result";
  cell_id: string;
  data: Record<string, unknown>;
  metadata: Record<string, unknown>;
}

export interface ErrorMessage {
  type: "error";
  cell_id: string;
  ename: string;
  evalue: string;
  traceback: string[];
}

export interface ExecuteReplyMessage {
  type: "execute_reply";
  cell_id: string;
  status: "ok" | "error";
  duration_ms: number;
}

export interface VariablesUpdateMessage {
  type: "variables_update";
  variables: Array<Record<string, unknown>>;
}

export interface KernelStatusMessage {
  type: "kernel_status";
  status: string;
  kernel_id?: string;
}

export interface CellStatesMessage {
  type: "cell_states";
  states: Record<string, string>;
  warnings: string[];
}

export type KernelWsMessage =
  | CellStatusMessage
  | StreamMessage
  | DisplayDataMessage
  | ExecuteResultMessage
  | ErrorMessage
  | ExecuteReplyMessage
  | VariablesUpdateMessage
  | KernelStatusMessage
  | CellStatesMessage;

/** /ws/filewatcher messages */

export interface CellModifiedMessage {
  type: "cell_modified";
  cell_id: string;
  new_content: string;
  new_hash: string;
}

export interface ManifestModifiedMessage {
  type: "manifest_modified";
  manifest: Record<string, unknown>;
}

export interface OutputAddedMessage {
  type: "output_added";
  output_type: string;
  path: string;
}

export type FileWatcherMessage =
  | CellModifiedMessage
  | ManifestModifiedMessage
  | OutputAddedMessage;
