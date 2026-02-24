import type { CellRunRequest, ExecutionResult } from "../types/execution";
import type { CellState } from "../types/cell";
import { get, post } from "./api";

export const executionApi = {
  runCell: (cellId: string) =>
    post<ExecutionResult>(`/run/${cellId}`),

  runRange: (data: CellRunRequest) =>
    post<ExecutionResult[]>("/run/range", data),

  runAll: () => post<ExecutionResult[]>("/run/all"),

  interrupt: () => post<{ status: string }>("/kernel/interrupt"),

  restart: () => post<{ status: string }>("/kernel/restart"),

  cellStates: () =>
    get<{ states: Record<string, CellState>; warnings: string[] }>("/cell-states"),
};
