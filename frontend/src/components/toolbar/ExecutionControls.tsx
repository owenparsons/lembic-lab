import { Play, SkipForward, FastForward, Square, RotateCcw } from "lucide-react";
import { ToolbarButton } from "./ToolbarButton";
import { useKernelStore } from "../../stores/kernelStore";
import { useNotebookStore } from "../../stores/notebookStore";
import { useUiStore } from "../../stores/uiStore";
import { executionApi } from "../../services/executionApi";

export function ExecutionControls() {
  const kernelStatus = useKernelStore((s) => s.status);
  const selectedCellId = useUiStore((s) => s.selectedCellId);
  const cells = useNotebookStore((s) => s.cells);
  const isBusy = kernelStatus === "busy";

  const handleRunSelected = async () => {
    if (!selectedCellId) return;
    await executionApi.runCell(selectedCellId);
  };

  const handleRunFromSelected = async () => {
    if (!selectedCellId) return;
    const idx = cells.findIndex((c) => c.id === selectedCellId);
    if (idx === -1) return;
    const cellIds = cells.slice(idx).map((c) => c.id);
    await executionApi.runRange({ cell_ids: cellIds });
  };

  const handleRunAll = async () => {
    await executionApi.runAll();
  };

  const handleInterrupt = async () => {
    await executionApi.interrupt();
  };

  const handleRestart = async () => {
    await executionApi.restart();
  };

  return (
    <div className="flex items-center gap-0.5">
      <ToolbarButton
        icon={Play}
        label="Run selected cell (Shift+Enter)"
        onClick={handleRunSelected}
        disabled={!selectedCellId || isBusy}
      />
      <ToolbarButton
        icon={SkipForward}
        label="Run from selected"
        onClick={handleRunFromSelected}
        disabled={!selectedCellId || isBusy}
      />
      <ToolbarButton
        icon={FastForward}
        label="Run all"
        onClick={handleRunAll}
        disabled={isBusy}
      />
      <div className="mx-1 h-4 w-px bg-df-border-secondary" />
      <ToolbarButton
        icon={Square}
        label="Interrupt kernel"
        onClick={handleInterrupt}
        disabled={!isBusy}
      />
      <ToolbarButton
        icon={RotateCcw}
        label="Restart kernel"
        onClick={handleRestart}
      />
    </div>
  );
}
