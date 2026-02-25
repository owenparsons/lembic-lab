import { useState, useRef, useEffect } from "react";
import { AlertTriangle } from "lucide-react";
import { useExecutionStore } from "../../stores/executionStore";
import { Tooltip } from "../shared/Tooltip";

export function WarningIndicator() {
  const warnings = useExecutionStore((s) => s.warnings);
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  // Close on click outside
  useEffect(() => {
    if (!open) return;
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [open]);

  if (warnings.length === 0) return null;

  return (
    <div ref={ref} className="relative">
      <Tooltip content={`${warnings.length} warning${warnings.length === 1 ? "" : "s"} — click to view`} position="bottom">
        <button
          onClick={() => setOpen((prev) => !prev)}
          className="flex items-center gap-1 rounded px-2 py-1 text-xs text-lb-state-stale transition-colors hover:bg-lb-bg-hover"
        >
          <AlertTriangle size={14} />
          <span>{warnings.length}</span>
        </button>
      </Tooltip>
      {open && (
        <div className="absolute right-0 top-full z-50 mt-1 w-80 rounded border border-lb-border-primary bg-lb-bg-elevated shadow-lg">
          <div className="border-b border-lb-border-secondary px-3 py-2 text-xs font-semibold text-lb-text-primary">
            Warnings ({warnings.length})
          </div>
          <ul className="max-h-60 overflow-y-auto py-1">
            {warnings.map((warning, i) => (
              <li
                key={i}
                className="flex items-start gap-2 px-3 py-1.5 text-xs text-lb-text-secondary"
              >
                <AlertTriangle size={12} className="mt-0.5 shrink-0 text-lb-state-stale" />
                <span>{warning}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
