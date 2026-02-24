import { useKernelStore } from "../../stores/kernelStore";
import { useNotebookStore } from "../../stores/notebookStore";
import { useTerminalStore } from "../../stores/terminalStore";

export function StatusBar() {
  const kernelStatus = useKernelStore((s) => s.status);
  const dirty = useNotebookStore((s) => s.dirty);
  const terminalConnected = useTerminalStore((s) => s.connected);

  const statusColor: Record<string, string> = {
    idle: "bg-df-state-success",
    busy: "bg-df-state-running",
    starting: "bg-df-state-stale",
    restarting: "bg-df-state-stale",
    dead: "bg-df-state-error",
    disconnected: "bg-df-text-muted",
  };

  return (
    <div className="flex h-6 items-center justify-between border-t border-df-border-secondary bg-df-bg-secondary px-3 text-xs text-df-text-muted">
      <div className="flex items-center gap-3">
        <span className="flex items-center gap-1.5">
          <span className={`inline-block h-2 w-2 rounded-full ${statusColor[kernelStatus] ?? "bg-df-text-muted"}`} />
          Kernel: {kernelStatus}
        </span>
        <span className="flex items-center gap-1.5">
          <span className={`inline-block h-2 w-2 rounded-full ${terminalConnected ? "bg-df-state-success" : "bg-df-text-muted"}`} />
          Terminal: {terminalConnected ? "connected" : "disconnected"}
        </span>
      </div>
      <div className="flex items-center gap-3">
        {dirty.size > 0 && (
          <span className="text-df-state-stale">
            {dirty.size} unsaved {dirty.size === 1 ? "cell" : "cells"}
          </span>
        )}
      </div>
    </div>
  );
}
