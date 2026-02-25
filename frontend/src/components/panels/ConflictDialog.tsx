import { useState } from "react";
import { AlertTriangle } from "lucide-react";
import { Modal } from "../shared/Modal";

interface ConflictDialogProps {
  cellId: string;
  cellName: string;
  localContent: string;
  externalContent: string;
  onAcceptLocal: () => void;
  onAcceptExternal: () => void;
  onDismiss: () => void;
}

/**
 * Conflict resolution dialog shown when a cell is modified externally
 * while the user has unsaved local changes.
 */
export function ConflictDialog({
  cellName,
  localContent,
  externalContent,
  onAcceptLocal,
  onAcceptExternal,
  onDismiss,
}: ConflictDialogProps) {
  const [view, setView] = useState<"side-by-side" | "local" | "external">(
    "side-by-side",
  );

  return (
    <Modal open={true} onClose={onDismiss} title={`Conflict in "${cellName}"`}>
      <div className="w-[800px] max-w-[90vw]">
        {/* Header */}
        <div className="flex items-center gap-3 border-b border-lb-border-primary px-4 py-3">
          <AlertTriangle size={18} className="text-lb-state-stale" />
          <div>
            <h2 className="text-sm font-semibold text-lb-text-primary">
              Conflict in "{cellName}"
            </h2>
            <p className="text-xs text-lb-text-muted">
              This cell was modified externally while you had unsaved changes.
            </p>
          </div>
        </div>

        {/* View tabs */}
        <div className="flex gap-1 border-b border-lb-border-primary px-4 py-1.5">
          {(
            [
              ["side-by-side", "Side by Side"],
              ["local", "Your Changes"],
              ["external", "External Changes"],
            ] as const
          ).map(([key, label]) => (
            <button
              key={key}
              onClick={() => setView(key)}
              className={`rounded px-2 py-1 text-xs transition-colors ${
                view === key
                  ? "bg-lb-accent-primary/20 text-lb-accent-primary"
                  : "text-lb-text-muted hover:text-lb-text-primary"
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="max-h-[400px] overflow-auto p-4">
          {view === "side-by-side" ? (
            <div className="grid grid-cols-2 gap-3">
              <div>
                <div className="mb-1 text-xs font-semibold text-lb-text-secondary">
                  Your Version
                </div>
                <pre className="rounded border border-lb-border-primary bg-lb-bg-tertiary p-2 text-xs text-lb-text-primary">
                  {localContent}
                </pre>
              </div>
              <div>
                <div className="mb-1 text-xs font-semibold text-lb-text-secondary">
                  External Version
                </div>
                <pre className="rounded border border-lb-border-primary bg-lb-bg-tertiary p-2 text-xs text-lb-text-primary">
                  {externalContent}
                </pre>
              </div>
            </div>
          ) : (
            <pre className="rounded border border-lb-border-primary bg-lb-bg-tertiary p-2 text-xs text-lb-text-primary">
              {view === "local" ? localContent : externalContent}
            </pre>
          )}
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-2 border-t border-lb-border-primary px-4 py-3">
          <button
            onClick={onDismiss}
            className="rounded px-3 py-1.5 text-xs text-lb-text-muted transition-colors hover:bg-lb-bg-hover hover:text-lb-text-primary"
          >
            Dismiss
          </button>
          <button
            onClick={onAcceptExternal}
            className="rounded border border-lb-border-primary bg-lb-bg-secondary px-3 py-1.5 text-xs text-lb-text-primary transition-colors hover:bg-lb-bg-hover"
          >
            Accept External
          </button>
          <button
            onClick={onAcceptLocal}
            className="rounded bg-lb-accent-secondary px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-lb-accent-primary"
          >
            Keep Mine
          </button>
        </div>
      </div>
    </Modal>
  );
}
