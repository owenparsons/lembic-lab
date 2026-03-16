export type CellType = "code" | "markdown" | "define";

export type CellState =
  | "idle"
  | "running"
  | "success"
  | "error"
  | "stale"
  | "stale_upstream";

export interface CellEntry {
  id: string;
  name: string;
  type: CellType;
  file: string;
}

export interface CellCreate {
  type?: CellType;
  name?: string;
  content?: string;
  after_id?: string;
}

export interface CellUpdate {
  name?: string;
  content?: string;
}

export interface CellAnnotation {
  text: string;
  style: "info" | "warning" | "success" | "error";
}

export interface NotebookSection {
  id: string;
  name: string;
  starts_at: string; // cell_id
  ends_at?: string | null; // cell_id where section ends (inclusive)
  collapsed: boolean;
}

export interface CellResponse {
  id: string;
  name: string;
  type: CellType;
  file: string;
  content: string;
  state: CellState;
  outputs: CellOutput[];
  annotation?: CellAnnotation | null;
  last_author?: string | null; // "user" | "external"
  last_modified?: string | null; // ISO 8601
}

export interface CellMoveRequest {
  after_id: string | null;
}

export type CellOutput =
  | StreamOutput
  | DisplayDataOutput
  | ExecuteResultOutput
  | ErrorOutput;

export interface StreamOutput {
  type: "stream";
  cell_id: string;
  stream: "stdout" | "stderr";
  text: string;
}

export interface DisplayDataOutput {
  type: "display_data";
  cell_id: string;
  data: Record<string, unknown>;
  metadata: Record<string, unknown>;
}

export interface ExecuteResultOutput {
  type: "execute_result";
  cell_id: string;
  data: Record<string, unknown>;
  metadata: Record<string, unknown>;
}

export interface ErrorOutput {
  type: "error";
  cell_id: string;
  ename: string;
  evalue: string;
  traceback: string[];
}
