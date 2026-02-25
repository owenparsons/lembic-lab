import { Play } from "lucide-react";
import type { CellResponse } from "../../types/cell";
import { CellStateIcon } from "./CellStateIcon";
import { IconButton } from "../shared/IconButton";
import { useExecutionStore } from "../../stores/executionStore";

interface CellHeaderProps {
  cell: CellResponse;
  onRun: () => void;
  isSelected: boolean;
}

export function CellHeader({ cell, onRun, isSelected }: CellHeaderProps) {
  const runningCellId = useExecutionStore((s) => s.runningCellId);
  const isRunning = runningCellId === cell.id;

  return (
    <div
      className={`flex items-center gap-2 rounded-t-md border-b px-3 py-1.5 ${
        isSelected
          ? "border-lb-accent-primary/30 bg-lb-bg-tertiary"
          : "border-lb-border-secondary bg-lb-bg-secondary"
      }`}
    >
      <CellStateIcon state={cell.state} />
      <span className="text-xs font-mono text-lb-text-muted">
        [{cell.id.slice(0, 4)}]
      </span>
      <span className="text-xs font-medium text-lb-text-secondary">
        {cell.name}
      </span>
      <span className="text-xs text-lb-text-muted">{cell.type}</span>
      <div className="flex-1" />
      {isRunning && (
        <span className="text-xs text-lb-state-running">running...</span>
      )}
      <IconButton
        icon={Play}
        label="Run cell"
        size={14}
        onClick={(e) => {
          e.stopPropagation();
          onRun();
        }}
      />
    </div>
  );
}
