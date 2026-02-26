import { useEffect } from "react";
import { useKernelStore } from "../../stores/kernelStore";
import { useNotebookStore } from "../../stores/notebookStore";
import { useTerminalStore } from "../../stores/terminalStore";
import { useEnvironmentStore } from "../../stores/environmentStore";
import { useUiStore } from "../../stores/uiStore";

export function StatusBar() {
  const kernelStatus = useKernelStore((s) => s.status);
  const dirty = useNotebookStore((s) => s.dirty);
  const sessions = useTerminalStore((s) => s.sessions);
  const activeSessionId = useTerminalStore((s) => s.activeSessionId);
  const terminalConnected =
    sessions.find((s) => s.id === activeSessionId)?.connected ?? false;
  const envStatus = useEnvironmentStore((s) => s.status);
  const loadStatus = useEnvironmentStore((s) => s.loadStatus);
  const togglePackagePanel = useUiStore((s) => s.togglePackagePanel);

  useEffect(() => {
    loadStatus();
  }, [loadStatus]);

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
        <button
          onClick={togglePackagePanel}
          className="flex items-center gap-1.5 hover:text-lb-text-primary"
        >
          <span className={`inline-block h-2 w-2 rounded-full ${envStatus?.exists ? "bg-lb-state-success" : "bg-lb-text-muted"}`} />
          {envStatus?.exists
            ? `Env: ${envStatus.package_count} packages`
            : "No env"}
        </button>
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
