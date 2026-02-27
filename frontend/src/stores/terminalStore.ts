import { create } from "zustand";
import type { TerminalAttachment } from "../types/terminal";

export interface TerminalSession {
  id: string;
  label: string;
  connected: boolean;
  initCommand?: string;
  isClaude?: boolean;
}

export interface NotebookSettings {
  close_terminal_on_exit: boolean;
}

let sessionCounter = 0;

interface TerminalState {
  sessions: TerminalSession[];
  activeSessionId: string | null;
  injectionMessage: string;
  attachments: TerminalAttachment[];
  settings: NotebookSettings;

  addSession: (options?: { initCommand?: string }) => string;
  removeSession: (id: string) => void;
  setActiveSession: (id: string) => void;
  setSessionConnected: (id: string, connected: boolean) => void;
  setSessionIsClaude: (id: string, isClaude: boolean) => void;
  setInjectionMessage: (message: string) => void;
  addAttachment: (attachment: TerminalAttachment) => void;
  removeAttachment: (cellId: string) => void;
  clearAttachments: () => void;
  clearInjection: () => void;
  fetchSettings: () => Promise<void>;
}

function generateSessionId(): string {
  return `term_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

export const useTerminalStore = create<TerminalState>((set, get) => ({
  sessions: [],
  activeSessionId: null,
  injectionMessage: "",
  attachments: [],
  settings: { close_terminal_on_exit: true },

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
    const { sessions, activeSessionId } = get();
    const remaining = sessions.filter((s) => s.id !== id);

    let nextActiveId: string | null = null;
    if (remaining.length > 0) {
      if (activeSessionId === id) {
        const idx = sessions.findIndex((s) => s.id === id);
        const adjacent = idx > 0 ? sessions[idx - 1] : sessions[idx + 1];
        nextActiveId = adjacent?.id ?? remaining[0]!.id;
      } else {
        nextActiveId = activeSessionId;
      }
    }

    set({ sessions: remaining, activeSessionId: nextActiveId });

    // Fire-and-forget DELETE to clean up backend PTY
    fetch(`/api/terminal/${id}`, { method: "DELETE" }).catch(() => {});
  },

  setActiveSession: (id) => {
    set({ activeSessionId: id });
  },

  setSessionConnected: (id, connected) =>
    set((state) => ({
      sessions: state.sessions.map((s) =>
        s.id === id ? { ...s, connected } : s,
      ),
    })),

  setSessionIsClaude: (id, isClaude) =>
    set((state) => ({
      sessions: state.sessions.map((s) =>
        s.id === id ? { ...s, isClaude } : s,
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

  fetchSettings: async () => {
    try {
      const res = await fetch("/api/notebook/settings");
      if (res.ok) {
        const data: NotebookSettings = await res.json();
        set({ settings: data });
      }
    } catch {
      // Keep defaults on failure
    }
  },
}));

// Fetch settings on module load
useTerminalStore.getState().fetchSettings();
