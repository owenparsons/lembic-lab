import type { CellOutput } from "./cell";

export type ExecutionStatus = "ok" | "error";

export interface CellRunRequest {
  cell_ids: string[];
}

export interface ExecutionResult {
  cell_id: string;
  status: ExecutionStatus;
  duration_ms: number;
  outputs: CellOutput[];
  error?: string;
}

export interface ExecutionEvent {
  cell_id: string;
  timestamp: string;
  status: ExecutionStatus;
  duration_ms: number;
  variables_defined: string[];
  variables_read: string[];
  error?: string;
}
