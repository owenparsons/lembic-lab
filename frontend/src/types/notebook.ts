import type { CellResponse } from "./cell";

export interface NotebookManifest {
  cells: CellResponse[];
}

export interface NotebookResponse {
  cells: CellResponse[];
}

export interface ReorderRequest {
  cell_ids: string[];
}
