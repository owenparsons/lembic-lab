import { Plus } from "lucide-react";
import { useNotebookStore } from "../../stores/notebookStore";
import { useUiStore } from "../../stores/uiStore";

interface AddCellButtonProps {
  afterId: string | null;
}

export function AddCellButton({ afterId }: AddCellButtonProps) {
  const addCell = useNotebookStore((s) => s.addCell);
  const selectCell = useUiStore((s) => s.selectCell);

  const handleAdd = async () => {
    const cell = await addCell({
      type: "code",
      after_id: afterId ?? undefined,
    });
    if (cell) {
      selectCell(cell.id);
    }
  };

  return (
    <div className="group flex items-center justify-center py-1">
      <button
        onClick={handleAdd}
        className="flex items-center gap-1 rounded-full border border-transparent px-3 py-0.5 text-xs text-df-text-muted opacity-0 transition-all hover:border-df-border-primary hover:bg-df-bg-secondary hover:text-df-text-secondary group-hover:opacity-100"
      >
        <Plus size={12} />
        <span>Add cell</span>
      </button>
    </div>
  );
}
