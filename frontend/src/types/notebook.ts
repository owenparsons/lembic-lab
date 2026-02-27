import type { CellResponse, NotebookSection } from "./cell";

export interface NotebookManifest {
  cells: CellResponse[];
  sections?: NotebookSection[];
}

export interface NotebookResponse {
  cells: CellResponse[];
  sections?: NotebookSection[];
}

export interface ReorderRequest {
  cell_ids: string[];
}
