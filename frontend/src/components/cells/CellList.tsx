import { useNotebookStore } from "../../stores/notebookStore";
import { useUiStore } from "../../stores/uiStore";
import { CodeCell } from "./CodeCell";
import { MarkdownCell } from "./MarkdownCell";
import { DefineCell } from "./DefineCell";
import { AddCellButton } from "./AddCellButton";
import { executionApi } from "../../services/executionApi";
import { Plus } from "lucide-react";

export function CellList() {
  const cells = useNotebookStore((s) => s.cells);
  const loading = useNotebookStore((s) => s.loading);
  const dirty = useNotebookStore((s) => s.dirty);
  const saveCell = useNotebookStore((s) => s.saveCell);
  const addCell = useNotebookStore((s) => s.addCell);
  const selectedCellId = useUiStore((s) => s.selectedCellId);
  const selectCell = useUiStore((s) => s.selectCell);
  const setMode = useUiStore((s) => s.setMode);

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center text-df-text-muted">
        Loading notebook...
      </div>
    );
  }

  if (cells.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-4 text-df-text-muted">
        <p>No cells yet</p>
        <button
          onClick={async () => {
            const cell = await addCell({ type: "code" });
            if (cell) {
              selectCell(cell.id);
              setMode("edit");
            }
          }}
          className="flex items-center gap-2 rounded-md border border-df-border-primary bg-df-bg-secondary px-4 py-2 text-sm text-df-text-primary transition-colors hover:bg-df-bg-hover"
        >
          <Plus size={16} />
          Add first cell
        </button>
      </div>
    );
  }

  const handleRunCell = async (cellId: string) => {
    // Save if dirty before running
    if (dirty.has(cellId)) {
      await saveCell(cellId);
    }
    await executionApi.runCell(cellId);
  };

  return (
    <div className="space-y-0 p-4">
      <AddCellButton afterId={null} />
      {cells.map((cell) => {
        const isSelected = selectedCellId === cell.id;
        const commonProps = {
          cell,
          isSelected,
          onRun: () => handleRunCell(cell.id),
        };

        return (
          <div
            key={cell.id}
            onClick={() => selectCell(cell.id)}
            className={`rounded-md border transition-colors ${
              isSelected
                ? "border-df-accent-primary/50"
                : "border-df-border-primary hover:border-df-border-primary/80"
            }`}
          >
            {cell.type === "markdown" ? (
              <MarkdownCell {...commonProps} />
            ) : cell.type === "define" ? (
              <DefineCell {...commonProps} />
            ) : (
              <CodeCell {...commonProps} />
            )}
            <AddCellButton afterId={cell.id} />
          </div>
        );
      })}
    </div>
  );
}
