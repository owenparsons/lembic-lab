import { create } from "zustand";
import type { CellState } from "../types/cell";
import type { ExecutionEvent } from "../types/execution";

interface ExecutionState {
  cellStates: Record<string, CellState>;
  logEntries: ExecutionEvent[];
  warnings: string[];
  runningCellId: string | null;
  runningStartTime: number | null;

  setCellStates: (states: Record<string, CellState>) => void;
  setCellState: (cellId: string, state: CellState) => void;
  setWarnings: (warnings: string[]) => void;
  addLogEntry: (entry: ExecutionEvent) => void;
  setRunning: (cellId: string | null) => void;
}

export const useExecutionStore = create<ExecutionState>((set) => ({
  cellStates: {},
  logEntries: [],
  warnings: [],
  runningCellId: null,
  runningStartTime: null,

  setCellStates: (states) => set({ cellStates: states }),

  setCellState: (cellId, state) =>
    set((prev) => ({
      cellStates: { ...prev.cellStates, [cellId]: state },
    })),

  setWarnings: (warnings) => set({ warnings }),

  addLogEntry: (entry) =>
    set((prev) => ({ logEntries: [...prev.logEntries, entry] })),

  setRunning: (cellId) =>
    set({
      runningCellId: cellId,
      runningStartTime: cellId ? Date.now() : null,
    }),
}));
