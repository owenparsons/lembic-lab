import { create } from "zustand";
import type { CellCreate, CellOutput, CellResponse, CellState, NotebookSection } from "../types/cell";
import { cellApi } from "../services/cellApi";
import { notebookApi } from "../services/notebookApi";

interface NotebookState {
  cells: CellResponse[];
  sections: NotebookSection[];
  contents: Record<string, string>; // cellId → current editor content
  dirty: Set<string>; // cells modified since last save
  loading: boolean;
  error: string | null;
  pendingRefresh: boolean;
  scrollToCellId: string | null;

  // Actions
  loadNotebook: () => Promise<void>;
  setPendingRefresh: (pending: boolean) => void;
  addCell: (data: CellCreate) => Promise<CellResponse | undefined>;
  deleteCell: (cellId: string) => Promise<void>;
  updateContent: (cellId: string, content: string) => void;
  saveCell: (cellId: string) => Promise<void>;
  saveAll: () => Promise<void>;
  setCellState: (cellId: string, state: CellState) => void;
  setCellOutputs: (cellId: string, outputs: CellOutput[]) => void;
  appendOutput: (cellId: string, output: CellOutput) => void;
  clearOutputs: (cellId: string) => void;
  setCells: (cells: CellResponse[]) => void;
  moveCell: (cellId: string, afterId: string | null) => Promise<void>;
  clearScrollTarget: () => void;
  toggleSection: (sectionId: string) => void;
}

export const useNotebookStore = create<NotebookState>((set, get) => ({
  cells: [],
  sections: [],
  contents: {},
  dirty: new Set(),
  loading: false,
  error: null,
  pendingRefresh: false,
  scrollToCellId: null,

  loadNotebook: async () => {
    const oldCells = get().cells;
    const oldCellIds = new Set(oldCells.map((c) => c.id));
    const isRefresh = oldCells.length > 0;
    // Only show loading spinner on initial load — refreshes keep cells mounted
    // so scroll position is preserved
    if (!isRefresh) {
      set({ loading: true, error: null });
    }
    try {
      const data = await notebookApi.load();
      const contents: Record<string, string> = {};
      for (const cell of data.cells) {
        contents[cell.id] = cell.content;
      }
      // Scroll to the last newly added cell (preserve existing target if set)
      const newCells = data.cells.filter((c) => !oldCellIds.has(c.id));
      const lastNew = newCells[newCells.length - 1];
      const scrollToCellId = lastNew?.id ?? get().scrollToCellId;
      set({ cells: data.cells, sections: data.sections ?? [], contents, dirty: new Set(), loading: false, error: null, pendingRefresh: false, scrollToCellId });
    } catch (e) {
      const message = e instanceof Error
        ? (e.name === "AbortError" ? "Backend not reachable (request timed out)" : e.message)
        : "Failed to load notebook";
      set({ loading: false, error: message });
    }
  },

  setPendingRefresh: (pending) => set({ pendingRefresh: pending }),

  addCell: async (data) => {
    try {
      const cell = await cellApi.create(data);
      set((state) => {
        const cells = [...state.cells];
        if (data.after_id) {
          const idx = cells.findIndex((c) => c.id === data.after_id);
          cells.splice(idx + 1, 0, cell);
        } else {
          cells.push(cell);
        }
        return {
          cells,
          contents: { ...state.contents, [cell.id]: cell.content },
          scrollToCellId: cell.id,
        };
      });
      return cell;
    } catch {
      return undefined;
    }
  },

  deleteCell: async (cellId) => {
    await cellApi.delete(cellId);
    set((state) => {
      const { [cellId]: _, ...contents } = state.contents;
      const dirty = new Set(state.dirty);
      dirty.delete(cellId);
      return {
        cells: state.cells.filter((c) => c.id !== cellId),
        contents,
        dirty,
      };
    });
  },

  updateContent: (cellId, content) => {
    set((state) => {
      const dirty = new Set(state.dirty);
      const original = state.cells.find((c) => c.id === cellId);
      if (original && original.content !== content) {
        dirty.add(cellId);
      } else {
        dirty.delete(cellId);
      }
      return {
        contents: { ...state.contents, [cellId]: content },
        dirty,
      };
    });
  },

  saveCell: async (cellId) => {
    const content = get().contents[cellId];
    if (content === undefined) return;
    await cellApi.update(cellId, { content });
    set((state) => {
      const dirty = new Set(state.dirty);
      dirty.delete(cellId);
      const cells = state.cells.map((c) =>
        c.id === cellId ? { ...c, content } : c,
      );
      return { cells, dirty };
    });
  },

  saveAll: async () => {
    const { dirty, contents } = get();
    const promises = Array.from(dirty).map((cellId) => {
      const content = contents[cellId];
      if (content !== undefined) {
        return cellApi.update(cellId, { content });
      }
      return Promise.resolve(undefined);
    });
    await Promise.all(promises);
    await notebookApi.save();
    set((state) => {
      const cells = state.cells.map((c) => {
        const content = state.contents[c.id];
        return content !== undefined ? { ...c, content } : c;
      });
      return { cells, dirty: new Set() };
    });
  },

  setCellState: (cellId, cellState) => {
    set((state) => ({
      cells: state.cells.map((c) =>
        c.id === cellId ? { ...c, state: cellState } : c,
      ),
    }));
  },

  setCellOutputs: (cellId, outputs) => {
    set((state) => ({
      cells: state.cells.map((c) =>
        c.id === cellId ? { ...c, outputs } : c,
      ),
    }));
  },

  appendOutput: (cellId, output) => {
    set((state) => ({
      cells: state.cells.map((c) =>
        c.id === cellId ? { ...c, outputs: [...c.outputs, output] } : c,
      ),
    }));
  },

  clearOutputs: (cellId) => {
    set((state) => ({
      cells: state.cells.map((c) =>
        c.id === cellId ? { ...c, outputs: [] } : c,
      ),
    }));
  },

  setCells: (cells) => set({ cells }),

  clearScrollTarget: () => set({ scrollToCellId: null }),

  toggleSection: (sectionId) => {
    set((state) => ({
      sections: state.sections.map((s) =>
        s.id === sectionId ? { ...s, collapsed: !s.collapsed } : s,
      ),
    }));
  },

  moveCell: async (cellId, afterId) => {
    await cellApi.move(cellId, { after_id: afterId });
    set((state) => {
      const cell = state.cells.find((c) => c.id === cellId);
      if (!cell) return state;
      const rest = state.cells.filter((c) => c.id !== cellId);
      if (afterId === null) {
        return { cells: [cell, ...rest] };
      }
      const idx = rest.findIndex((c) => c.id === afterId);
      rest.splice(idx + 1, 0, cell);
      return { cells: rest };
    });
  },
}));
