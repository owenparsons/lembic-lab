import { create } from "zustand";
import type { TerminalAttachment } from "../types/terminal";

interface TerminalState {
  connected: boolean;
  injectionMessage: string;
  attachments: TerminalAttachment[];

  setConnected: (connected: boolean) => void;
  setInjectionMessage: (message: string) => void;
  addAttachment: (attachment: TerminalAttachment) => void;
  removeAttachment: (cellId: string) => void;
  clearAttachments: () => void;
  clearInjection: () => void;
}

export const useTerminalStore = create<TerminalState>((set) => ({
  connected: false,
  injectionMessage: "",
  attachments: [],

  setConnected: (connected) => set({ connected }),

  setInjectionMessage: (message) => set({ injectionMessage: message }),

  addAttachment: (attachment) =>
    set((state) => {
      // Don't add duplicates
      if (state.attachments.some((a) => a.cell_id === attachment.cell_id)) {
        return state;
      }
      return { attachments: [...state.attachments, attachment] };
    }),

  removeAttachment: (cellId) =>
    set((state) => ({
      attachments: state.attachments.filter((a) => a.cell_id !== cellId),
    })),

  clearAttachments: () => set({ attachments: [] }),

  clearInjection: () => set({ injectionMessage: "", attachments: [] }),
}));
