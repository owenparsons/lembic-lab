import { AlertTriangle } from "lucide-react";
import { useExecutionStore } from "../../stores/executionStore";
import { Tooltip } from "../shared/Tooltip";

export function WarningIndicator() {
  const warnings = useExecutionStore((s) => s.warnings);

  if (warnings.length === 0) return null;

  return (
    <Tooltip content={`${warnings.length} warning${warnings.length === 1 ? "" : "s"}`}>
      <div className="flex items-center gap-1 rounded px-2 py-1 text-xs text-lb-state-stale">
        <AlertTriangle size={14} />
        <span>{warnings.length}</span>
      </div>
    </Tooltip>
  );
}
