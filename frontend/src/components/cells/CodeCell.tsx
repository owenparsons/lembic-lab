import type { CellResponse } from "../../types/cell";
import { CellHeader } from "./CellHeader";
import { CellOutput } from "./CellOutput";
import { MonacoWrapper } from "../editor/MonacoWrapper";
import { useNotebookStore } from "../../stores/notebookStore";
import { useUiStore } from "../../stores/uiStore";

interface CodeCellProps {
  cell: CellResponse;
  isSelected: boolean;
  onRun: () => void;
}

export function CodeCell({ cell, isSelected, onRun }: CodeCellProps) {
  const updateContent = useNotebookStore((s) => s.updateContent);
  const contents = useNotebookStore((s) => s.contents);
  const mode = useUiStore((s) => s.mode);
  const setMode = useUiStore((s) => s.setMode);
  const selectCell = useUiStore((s) => s.selectCell);

  const content = contents[cell.id] ?? cell.content;
  const isEditing = isSelected && mode === "edit";

  const handleRunAndAdvance = () => {
    onRun();
    // TODO: advance to next cell
  };

  return (
    <div>
      <CellHeader cell={cell} onRun={onRun} isSelected={isSelected} />
      {isEditing ? (
        <MonacoWrapper
          value={content}
          onChange={(v) => updateContent(cell.id, v)}
          onRun={onRun}
          onRunAndAdvance={handleRunAndAdvance}
          onEscape={() => setMode("command")}
        />
      ) : (
        <div
          className="cursor-pointer rounded-b-md bg-df-bg-tertiary px-3 py-2"
          onClick={() => {
            selectCell(cell.id);
            setMode("edit");
          }}
        >
          <pre className="whitespace-pre-wrap font-mono text-xs text-df-text-primary">
            {content || "\u00A0"}
          </pre>
        </div>
      )}
      <CellOutput outputs={cell.outputs} />
    </div>
  );
}
