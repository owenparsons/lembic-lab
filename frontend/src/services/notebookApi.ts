import type { NotebookResponse, ReorderRequest } from "../types/notebook";
import { get, post } from "./api";

export const notebookApi = {
  load: () => get<NotebookResponse>("/notebook"),

  save: () => post<{ status: string }>("/notebook/save"),

  reorder: (data: ReorderRequest) =>
    post<{ status: string }>("/notebook/reorder", data),
};
