import { useState } from "react";
import { ChevronRight, ChevronDown } from "lucide-react";
import type { CellResponse } from "../../types/cell";
import { CellAnnotationBanner } from "./CellAnnotationBanner";
import { CellHeader } from "./CellHeader";
import { MonacoWrapper } from "../editor/MonacoWrapper";
import { useNotebookStore } from "../../stores/notebookStore";

interface DefineCellProps {
  cell: CellResponse;
  isSelected: boolean;
  onRun: () => void;
}

export function DefineCell({ cell, isSelected, onRun }: DefineCellProps) {
  const [expanded, setExpanded] = useState(false);
  const contents = useNotebookStore((s) => s.contents);
  const updateContent = useNotebookStore((s) => s.updateContent);
  const content = contents[cell.id] ?? cell.content;

  // Extract function name from content (rough heuristic)
  const fnMatch = content.match(/^def\s+(\w+)/m);
  const fnName = fnMatch ? fnMatch[1] : cell.name;

  return (
    <div>
      {cell.annotation && <CellAnnotationBanner annotation={cell.annotation} />}
      <CellHeader cell={cell} onRun={onRun} isSelected={isSelected} />
      <div
        className="flex cursor-pointer items-center gap-2 rounded-b-md bg-lb-bg-secondary px-3 py-2"
        onClick={() => setExpanded(!expanded)}
      >
        {expanded ? (
          <ChevronDown size={14} className="text-lb-text-muted" />
        ) : (
          <ChevronRight size={14} className="text-lb-text-muted" />
        )}
        <span className="font-mono text-xs text-lb-syntax-function">
          DEFINE
        </span>
        <span className="font-mono text-xs text-lb-text-primary">
          {fnName}()
        </span>
      </div>
      {expanded && (
        <MonacoWrapper
          value={content}
          onChange={(v) => updateContent(cell.id, v)}
          onRun={onRun}
        />
      )}
    </div>
  );
}
