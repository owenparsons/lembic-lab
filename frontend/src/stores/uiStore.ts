import { create } from "zustand";
import { persist } from "zustand/middleware";

export type PanelTab = "variables" | "dependencies" | "profile" | "packages";

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
  packagePanelOpen: boolean;
  activePanelTab: PanelTab | null;
  confirmOnRefresh: boolean;

  setActivePanelTab: (tab: PanelTab | null) => void;
  togglePaneOrder: () => void;
  setPaneSize: (size: number) => void;
  selectCell: (cellId: string | null) => void;
  setMode: (mode: Mode) => void;
  toggleVariableExplorer: () => void;
  toggleProfilePanel: () => void;
  toggleDependencyGraph: () => void;
  togglePackagePanel: () => void;
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
      packagePanelOpen: false,
      activePanelTab: null,
      confirmOnRefresh: false,

      setActivePanelTab: (tab) => set({ activePanelTab: tab }),

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
            activePanelTab: opening
              ? "variables"
              : state.activePanelTab === "variables"
                ? null
                : state.activePanelTab,
          };
        }),

      toggleProfilePanel: () =>
        set((state) => {
          const opening = !state.profilePanelOpen;
          return {
            profilePanelOpen: opening,
            activePanelTab: opening
              ? "profile"
              : state.activePanelTab === "profile"
                ? null
                : state.activePanelTab,
          };
        }),

      toggleDependencyGraph: () =>
        set((state) => {
          const opening = !state.dependencyGraphOpen;
          return {
            dependencyGraphOpen: opening,
            activePanelTab: opening
              ? "dependencies"
              : state.activePanelTab === "dependencies"
                ? null
                : state.activePanelTab,
          };
        }),

      togglePackagePanel: () =>
        set((state) => {
          const opening = !state.packagePanelOpen;
          return {
            packagePanelOpen: opening,
            activePanelTab: opening
              ? "packages"
              : state.activePanelTab === "packages"
                ? null
                : state.activePanelTab,
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
