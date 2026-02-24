import { create } from "zustand";
import type { KernelStatus } from "../types/kernel";
import { executionApi } from "../services/executionApi";

interface KernelState {
  status: KernelStatus;
  executionQueue: string[]; // cell IDs pending execution
  sessionStartTime: number | null;

  setStatus: (status: KernelStatus) => void;
  interrupt: () => Promise<void>;
  restart: () => Promise<void>;
  enqueue: (cellIds: string[]) => void;
  dequeue: (cellId: string) => void;
  clearQueue: () => void;
  startSession: () => void;
}

export const useKernelStore = create<KernelState>((set) => ({
  status: "disconnected",
  executionQueue: [],
  sessionStartTime: null,

  setStatus: (status) => set({ status }),

  interrupt: async () => {
    await executionApi.interrupt();
  },

  restart: async () => {
    set({ status: "restarting" });
    await executionApi.restart();
    set({ status: "idle" });
  },

  enqueue: (cellIds) =>
    set((state) => ({
      executionQueue: [...state.executionQueue, ...cellIds],
    })),

  dequeue: (cellId) =>
    set((state) => ({
      executionQueue: state.executionQueue.filter((id) => id !== cellId),
    })),

  clearQueue: () => set({ executionQueue: [] }),

  startSession: () => set({ sessionStartTime: Date.now() }),
}));
