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

  history: (cellId: string) =>
    get<Array<{ cell_id: string; timestamp: number; size: number }>>(`/cells/${cellId}/history`),

  historyVersion: (cellId: string, timestamp: number) =>
    get<{ cell_id: string; timestamp: number; content: string }>(`/cells/${cellId}/history/${timestamp}`),
};
