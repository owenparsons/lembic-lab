import type { CellCreate, CellMoveRequest, CellResponse, CellUpdate } from "../types/cell";
import { del, get, post, put } from "./api";

export const cellApi = {
  list: () => get<CellResponse[]>("/cells"),

  get: (cellId: string) => get<CellResponse>(`/cells/${cellId}`),

  create: (data: CellCreate) => post<CellResponse>("/cells", data),

  update: (cellId: string, data: CellUpdate) =>
    put<CellResponse>(`/cells/${cellId}`, data),

  delete: (cellId: string) => del<{ status: string }>(`/cells/${cellId}`),

  move: (cellId: string, data: CellMoveRequest) =>
    post<{ status: string }>(`/cells/${cellId}/move`, data),
};
