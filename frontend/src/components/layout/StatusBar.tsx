import { useKernelStore } from "../../stores/kernelStore";
import { useNotebookStore } from "../../stores/notebookStore";
import { useTerminalStore } from "../../stores/terminalStore";

export function StatusBar() {
  const kernelStatus = useKernelStore((s) => s.status);
  const dirty = useNotebookStore((s) => s.dirty);
  const terminalConnected = useTerminalStore((s) => s.connected);

  const statusColor: Record<string, string> = {
    idle: "bg-lb-state-success",
    busy: "bg-lb-state-running",
    starting: "bg-lb-state-stale",
    restarting: "bg-lb-state-stale",
    dead: "bg-lb-state-error",
    disconnected: "bg-lb-text-muted",
  };

  return (
    <div className="flex h-6 items-center justify-between border-t border-lb-border-secondary bg-lb-bg-secondary px-3 text-xs text-lb-text-muted">
      <div className="flex items-center gap-3">
        <span className="flex items-center gap-1.5">
          <span className={`inline-block h-2 w-2 rounded-full ${statusColor[kernelStatus] ?? "bg-lb-text-muted"}`} />
          Kernel: {kernelStatus}
        </span>
        <span className="flex items-center gap-1.5">
          <span className={`inline-block h-2 w-2 rounded-full ${terminalConnected ? "bg-lb-state-success" : "bg-lb-text-muted"}`} />
          Terminal: {terminalConnected ? "connected" : "disconnected"}
        </span>
      </div>
      <div className="flex items-center gap-3">
        {dirty.size > 0 && (
          <span className="text-lb-state-stale">
            {dirty.size} unsaved {dirty.size === 1 ? "cell" : "cells"}
          </span>
        )}
      </div>
    </div>
  );
}
