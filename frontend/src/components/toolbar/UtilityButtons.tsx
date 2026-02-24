import { Save, Variable, GitBranch } from "lucide-react";
import { ToolbarButton } from "./ToolbarButton";
import { useNotebookStore } from "../../stores/notebookStore";
import { useUiStore } from "../../stores/uiStore";

export function UtilityButtons() {
  const saveAll = useNotebookStore((s) => s.saveAll);
  const dirty = useNotebookStore((s) => s.dirty);
  const toggleVarExplorer = useUiStore((s) => s.toggleVariableExplorer);
  const toggleDepGraph = useUiStore((s) => s.toggleDependencyGraph);
  const varExplorerOpen = useUiStore((s) => s.variableExplorerOpen);
  const depGraphOpen = useUiStore((s) => s.dependencyGraphOpen);

  return (
    <div className="flex items-center gap-0.5">
      <ToolbarButton
        icon={Save}
        label="Save all (Cmd+S)"
        onClick={saveAll}
        disabled={dirty.size === 0}
      />
      <div className="mx-1 h-4 w-px bg-df-border-secondary" />
      <ToolbarButton
        icon={Variable}
        label="Variable explorer"
        onClick={toggleVarExplorer}
        active={varExplorerOpen}
      />
      <ToolbarButton
        icon={GitBranch}
        label="Dependency graph"
        onClick={toggleDepGraph}
        active={depGraphOpen}
      />
    </div>
  );
}
