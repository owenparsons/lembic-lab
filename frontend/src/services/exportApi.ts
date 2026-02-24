import { post } from "./api";

export interface ExportResult {
  format: string;
  path: string;
  message: string;
}

export const exportApi = {
  exportNotebook: (format: "ipynb" | "python" | "package") =>
    post<ExportResult>("/export", { format }),
};
