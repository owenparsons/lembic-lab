import { create } from "zustand";
import type { TerminalAttachment } from "../types/terminal";

export interface TerminalSession {
  id: string;
  label: string;
  connected: boolean;
  initCommand?: string;
}

let sessionCounter = 0;

interface TerminalState {
  sessions: TerminalSession[];
  activeSessionId: string | null;
  injectionMessage: string;
  attachments: TerminalAttachment[];

  addSession: (options?: { initCommand?: string }) => string;
  removeSession: (id: string) => void;
  setActiveSession: (id: string) => void;
  setSessionConnected: (id: string, connected: boolean) => void;
  setInjectionMessage: (message: string) => void;
  addAttachment: (attachment: TerminalAttachment) => void;
  removeAttachment: (cellId: string) => void;
  clearAttachments: () => void;
  clearInjection: () => void;
}

function generateSessionId(): string {
  return `term_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

export const useTerminalStore = create<TerminalState>((set, get) => ({
  sessions: [],
  activeSessionId: null,
  injectionMessage: "",
  attachments: [],

  addSession: (options) => {
    sessionCounter++;
    const session: TerminalSession = {
      id: generateSessionId(),
      label: `Terminal ${sessionCounter}`,
      connected: false,
      initCommand: options?.initCommand,
    };
    set((state) => ({
      sessions: [...state.sessions, session],
      activeSessionId: session.id,
    }));
    return session.id;
  },

  removeSession: (id) => {
    const { sessions, activeSessionId, addSession } = get();

    // If closing the last tab, create a new one first
    if (sessions.length === 1) {
      const newId = addSession();
      set((state) => ({
        sessions: state.sessions.filter((s) => s.id !== id),
        activeSessionId: newId,
      }));
    } else {
      // Switch to adjacent tab if closing the active one
      let nextActiveId = activeSessionId;
      if (activeSessionId === id) {
        const idx = sessions.findIndex((s) => s.id === id);
        const adjacent = idx > 0 ? sessions[idx - 1] : sessions[idx + 1];
        nextActiveId = adjacent?.id ?? activeSessionId;
      }
      set((state) => ({
        sessions: state.sessions.filter((s) => s.id !== id),
        activeSessionId: nextActiveId,
      }));
    }

    // Fire-and-forget DELETE to clean up backend PTY
    fetch(`/api/terminal/${id}`, { method: "DELETE" }).catch(() => {});
  },

  setActiveSession: (id) => set({ activeSessionId: id }),

  setSessionConnected: (id, connected) =>
    set((state) => ({
      sessions: state.sessions.map((s) =>
        s.id === id ? { ...s, connected } : s,
      ),
    })),

  setInjectionMessage: (message) => set({ injectionMessage: message }),

  addAttachment: (attachment) =>
    set((state) => {
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
