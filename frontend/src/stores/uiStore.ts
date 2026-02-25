import { create } from "zustand";
import { persist } from "zustand/middleware";

type PaneOrder = "notebook-terminal" | "terminal-notebook";
type Mode = "command" | "edit";

interface UiState {
  paneOrder: PaneOrder;
  notebookPaneSize: number; // percentage
  selectedCellId: string | null;
  mode: Mode;
  variableExplorerOpen: boolean;
  profilePanelOpen: boolean;
  dependencyGraphOpen: boolean;
  confirmOnRefresh: boolean;

  togglePaneOrder: () => void;
  setPaneSize: (size: number) => void;
  selectCell: (cellId: string | null) => void;
  setMode: (mode: Mode) => void;
  toggleVariableExplorer: () => void;
  toggleProfilePanel: () => void;
  toggleDependencyGraph: () => void;
  toggleConfirmOnRefresh: () => void;
}

export const useUiStore = create<UiState>()(
  persist(
    (set) => ({
      paneOrder: "notebook-terminal",
      notebookPaneSize: 60,
      selectedCellId: null,
      mode: "command",
      variableExplorerOpen: false,
      profilePanelOpen: false,
      dependencyGraphOpen: false,
      confirmOnRefresh: false,

      togglePaneOrder: () =>
        set((state) => ({
          paneOrder:
            state.paneOrder === "notebook-terminal"
              ? "terminal-notebook"
              : "notebook-terminal",
        })),

      setPaneSize: (size) => set({ notebookPaneSize: size }),

      selectCell: (cellId) => set({ selectedCellId: cellId }),

      setMode: (mode) => set({ mode }),

      toggleVariableExplorer: () =>
        set((state) => ({ variableExplorerOpen: !state.variableExplorerOpen })),

      toggleProfilePanel: () =>
        set((state) => ({ profilePanelOpen: !state.profilePanelOpen })),

      toggleDependencyGraph: () =>
        set((state) => ({ dependencyGraphOpen: !state.dependencyGraphOpen })),

      toggleConfirmOnRefresh: () =>
        set((state) => ({ confirmOnRefresh: !state.confirmOnRefresh })),
    }),
    {
      name: "dataflow-ui",
      partialize: (state) => ({
        paneOrder: state.paneOrder,
        notebookPaneSize: state.notebookPaneSize,
        variableExplorerOpen: state.variableExplorerOpen,
        confirmOnRefresh: state.confirmOnRefresh,
      }),
    },
  ),
);
