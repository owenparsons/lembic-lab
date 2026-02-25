import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { CellResponse } from "../../types/cell";
import { CellHeader } from "./CellHeader";
import { MonacoWrapper } from "../editor/MonacoWrapper";
import { useNotebookStore } from "../../stores/notebookStore";

interface MarkdownCellProps {
  cell: CellResponse;
  isSelected: boolean;
  onRun: () => void;
}

export function MarkdownCell({ cell, isSelected, onRun }: MarkdownCellProps) {
  const [editing, setEditing] = useState(false);
  const updateContent = useNotebookStore((s) => s.updateContent);
  const contents = useNotebookStore((s) => s.contents);
  const content = contents[cell.id] ?? cell.content;

  return (
    <div>
      <CellHeader cell={cell} onRun={onRun} isSelected={isSelected} />
      {editing ? (
        <MonacoWrapper
          value={content}
          onChange={(v) => updateContent(cell.id, v)}
          language="markdown"
          onEscape={() => setEditing(false)}
          onRun={() => {
            setEditing(false);
            onRun();
          }}
        />
      ) : (
        <div
          className="prose prose-invert max-w-none cursor-pointer rounded-b-md bg-lb-bg-secondary px-4 py-3 text-sm text-lb-text-primary"
          onDoubleClick={() => setEditing(true)}
        >
          {content ? (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
          ) : (
            <p className="text-lb-text-muted italic">Double-click to edit markdown</p>
          )}
        </div>
      )}
    </div>
  );
}
