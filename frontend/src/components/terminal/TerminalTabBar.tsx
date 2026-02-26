import { Plus, Terminal, X, Database, GitBranch, BarChart3, Package } from "lucide-react";
import { useTerminalStore } from "../../stores/terminalStore";
import { useUiStore, type PanelTab } from "../../stores/uiStore";

const PANEL_TABS: {
  key: PanelTab;
  label: string;
  icon: typeof Database;
  openKey: "variableExplorerOpen" | "dependencyGraphOpen" | "profilePanelOpen" | "packagePanelOpen";
  toggleKey: "toggleVariableExplorer" | "toggleDependencyGraph" | "toggleProfilePanel" | "togglePackagePanel";
}[] = [
  { key: "variables", label: "Variables", icon: Database, openKey: "variableExplorerOpen", toggleKey: "toggleVariableExplorer" },
  { key: "dependencies", label: "Dependencies", icon: GitBranch, openKey: "dependencyGraphOpen", toggleKey: "toggleDependencyGraph" },
  { key: "profile", label: "Data Profile", icon: BarChart3, openKey: "profilePanelOpen", toggleKey: "toggleProfilePanel" },
  { key: "packages", label: "Packages", icon: Package, openKey: "packagePanelOpen", toggleKey: "togglePackagePanel" },
];

export function TerminalTabBar() {
  const { sessions, addSession, removeSession, setActiveSession } =
    useTerminalStore();
  const activeSessionId = useTerminalStore((s) => s.activeSessionId);
  const activePanelTab = useUiStore((s) => s.activePanelTab);
  const setActivePanelTab = useUiStore((s) => s.setActivePanelTab);
  const variableExplorerOpen = useUiStore((s) => s.variableExplorerOpen);
  const dependencyGraphOpen = useUiStore((s) => s.dependencyGraphOpen);
  const profilePanelOpen = useUiStore((s) => s.profilePanelOpen);
  const packagePanelOpen = useUiStore((s) => s.packagePanelOpen);
  const toggleVariableExplorer = useUiStore((s) => s.toggleVariableExplorer);
  const toggleDependencyGraph = useUiStore((s) => s.toggleDependencyGraph);
  const toggleProfilePanel = useUiStore((s) => s.toggleProfilePanel);
  const togglePackagePanel = useUiStore((s) => s.togglePackagePanel);

  const openState: Record<string, boolean> = {
    variableExplorerOpen,
    dependencyGraphOpen,
    profilePanelOpen,
    packagePanelOpen,
  };
  const toggleFns: Record<string, () => void> = {
    toggleVariableExplorer,
    toggleDependencyGraph,
    toggleProfilePanel,
    togglePackagePanel,
  };

  return (
    <div className="flex items-center border-b border-lb-border-secondary bg-lb-bg-secondary">
      <div className="flex min-w-0 flex-1 overflow-x-auto">
        {sessions.map((session) => {
          const isActive =
            activeSessionId === session.id && !activePanelTab;
          return (
            <button
              key={session.id}
              onClick={() => {
                setActiveSession(session.id);
                setActivePanelTab(null);
              }}
              className={`group flex shrink-0 items-center gap-1.5 border-r border-lb-border-secondary px-3 py-1.5 text-xs font-medium transition-colors ${
                isActive
                  ? "bg-lb-bg-primary text-lb-text-primary"
                  : "bg-lb-bg-secondary text-lb-text-secondary hover:bg-lb-bg-tertiary"
              }`}
            >
              <Terminal size={12} className="shrink-0 text-lb-text-secondary" />
              <span className="truncate">{session.label}</span>
              <span
                className={`inline-block h-1.5 w-1.5 shrink-0 rounded-full ${
                  session.connected
                    ? "bg-lb-state-success"
                    : "bg-lb-text-muted"
                }`}
              />
              <span
                role="button"
                onClick={(e) => {
                  e.stopPropagation();
                  removeSession(session.id);
                }}
                className="shrink-0 rounded p-0.5 opacity-0 transition-opacity hover:bg-lb-bg-tertiary group-hover:opacity-100"
              >
                <X size={10} />
              </span>
            </button>
          );
        })}

        {/* Panel tabs */}
        {PANEL_TABS.map(({ key, label, icon: Icon, openKey, toggleKey }) => {
          if (!openState[openKey]) return null;
          const isActive = activePanelTab === key;
          return (
            <button
              key={key}
              onClick={() => setActivePanelTab(key)}
              className={`group flex shrink-0 items-center gap-1.5 border-r border-lb-border-secondary px-3 py-1.5 text-xs font-medium transition-colors ${
                isActive
                  ? "bg-lb-bg-primary text-lb-text-primary"
                  : "bg-lb-bg-secondary text-lb-text-secondary hover:bg-lb-bg-tertiary"
              }`}
            >
              <Icon size={12} className="shrink-0 text-lb-text-secondary" />
              <span className="truncate">{label}</span>
              <span
                role="button"
                onClick={(e) => {
                  e.stopPropagation();
                  toggleFns[toggleKey]!();
                }}
                className="shrink-0 rounded p-0.5 opacity-0 transition-opacity hover:bg-lb-bg-tertiary group-hover:opacity-100"
              >
                <X size={10} />
              </span>
            </button>
          );
        })}
      </div>
      <button
        onClick={() => {
          addSession();
          setActivePanelTab(null);
        }}
        className="shrink-0 px-2 py-1.5 text-lb-text-secondary transition-colors hover:bg-lb-bg-tertiary hover:text-lb-text-primary"
        title="New terminal"
      >
        <Plus size={14} />
      </button>
    </div>
  );
}
