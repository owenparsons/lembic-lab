import { create } from "zustand";
import { persist } from "zustand/middleware";

export type PanelTab = "variables" | "dependencies" | "profile";

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
  activeRightTab: string | null;
  confirmOnRefresh: boolean;

  setActiveRightTab: (tab: string | null) => void;
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
      activeRightTab: null,
      confirmOnRefresh: false,

      setActiveRightTab: (tab) => set({ activeRightTab: tab }),

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
        set((state) => {
          const opening = !state.variableExplorerOpen;
          return {
            variableExplorerOpen: opening,
            activeRightTab: opening
              ? "variables"
              : state.activeRightTab === "variables"
                ? null
                : state.activeRightTab,
          };
        }),

      toggleProfilePanel: () =>
        set((state) => {
          const opening = !state.profilePanelOpen;
          return {
            profilePanelOpen: opening,
            activeRightTab: opening
              ? "profile"
              : state.activeRightTab === "profile"
                ? null
                : state.activeRightTab,
          };
        }),

      toggleDependencyGraph: () =>
        set((state) => {
          const opening = !state.dependencyGraphOpen;
          return {
            dependencyGraphOpen: opening,
            activeRightTab: opening
              ? "dependencies"
              : state.activeRightTab === "dependencies"
                ? null
                : state.activeRightTab,
          };
        }),

      toggleConfirmOnRefresh: () =>
        set((state) => ({ confirmOnRefresh: !state.confirmOnRefresh })),
    }),
    {
      name: "lembic-ui",
      partialize: (state) => ({
        paneOrder: state.paneOrder,
        notebookPaneSize: state.notebookPaneSize,
        variableExplorerOpen: state.variableExplorerOpen,
        confirmOnRefresh: state.confirmOnRefresh,
      }),
    },
  ),
);
