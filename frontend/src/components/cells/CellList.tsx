import { useNotebookStore } from "../../stores/notebookStore";
import { useUiStore } from "../../stores/uiStore";
import { Plus } from "lucide-react";

export function CellList() {
  const cells = useNotebookStore((s) => s.cells);
  const loading = useNotebookStore((s) => s.loading);
  const { addCell } = useNotebookStore();
  const selectCell = useUiStore((s) => s.selectCell);

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
            if (cell) selectCell(cell.id);
          }}
          className="flex items-center gap-2 rounded-md border border-df-border-primary bg-df-bg-secondary px-4 py-2 text-sm text-df-text-primary transition-colors hover:bg-df-bg-hover"
        >
          <Plus size={16} />
          Add first cell
        </button>
      </div>
    );
  }

  return (
    <div className="p-4 text-df-text-muted">
      {/* Cell rendering will be implemented in Phase 1.16-1.17 */}
      <p className="text-sm">{cells.length} cell{cells.length !== 1 ? "s" : ""} loaded</p>
    </div>
  );
}
