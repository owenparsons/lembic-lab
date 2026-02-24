import { Terminal } from "lucide-react";
import { useTerminalStore } from "../../stores/terminalStore";

export function TerminalHeader() {
  const connected = useTerminalStore((s) => s.connected);

  return (
    <div className="flex items-center gap-2 border-b border-df-border-secondary bg-df-bg-secondary px-3 py-1.5">
      <Terminal size={14} className="text-df-text-secondary" />
      <span className="text-xs font-medium text-df-text-secondary">Terminal</span>
      <span
        className={`inline-block h-1.5 w-1.5 rounded-full ${connected ? "bg-df-state-success" : "bg-df-text-muted"}`}
      />
    </div>
  );
}
