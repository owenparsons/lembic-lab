import { Plus, Trash2, ArrowUp, ArrowDown } from "lucide-react";
import { ToolbarButton } from "./ToolbarButton";
import { useNotebookStore } from "../../stores/notebookStore";
import { useUiStore } from "../../stores/uiStore";

export function CellOperations() {
  const { addCell, deleteCell, cells, moveCell } = useNotebookStore();
  const { selectedCellId, selectCell } = useUiStore();

  const handleAddCell = async () => {
    const cell = await addCell({
      type: "code",
      after_id: selectedCellId ?? undefined,
    });
    if (cell) {
      selectCell(cell.id);
    }
  };

  const handleDeleteCell = async () => {
    if (!selectedCellId) return;
    const idx = cells.findIndex((c) => c.id === selectedCellId);
    await deleteCell(selectedCellId);
    // Select next cell or previous
    if (cells.length > 1) {
      const nextIdx = Math.min(idx, cells.length - 2);
      const next = cells.filter((c) => c.id !== selectedCellId)[nextIdx];
      selectCell(next?.id ?? null);
    } else {
      selectCell(null);
    }
  };

  const handleMoveUp = async () => {
    if (!selectedCellId) return;
    const idx = cells.findIndex((c) => c.id === selectedCellId);
    if (idx <= 0) return;
    const afterId = idx >= 2 ? (cells[idx - 2]?.id ?? null) : null;
    await moveCell(selectedCellId, afterId);
  };

  const handleMoveDown = async () => {
    if (!selectedCellId) return;
    const idx = cells.findIndex((c) => c.id === selectedCellId);
    if (idx === -1 || idx >= cells.length - 1) return;
    const afterId = cells[idx + 1]?.id ?? null;
    await moveCell(selectedCellId, afterId);
  };

  return (
    <div className="flex items-center gap-0.5">
      <ToolbarButton icon={Plus} label="Add cell (B)" onClick={handleAddCell} />
      <ToolbarButton
        icon={Trash2}
        label="Delete cell (DD)"
        onClick={handleDeleteCell}
        disabled={!selectedCellId}
      />
      <div className="mx-1 h-4 w-px bg-df-border-secondary" />
      <ToolbarButton
        icon={ArrowUp}
        label="Move cell up"
        onClick={handleMoveUp}
        disabled={!selectedCellId}
      />
      <ToolbarButton
        icon={ArrowDown}
        label="Move cell down"
        onClick={handleMoveDown}
        disabled={!selectedCellId}
      />
    </div>
  );
}
