import { Plus, Terminal, X } from "lucide-react";
import { useTerminalStore } from "../../stores/terminalStore";

export function TerminalTabBar() {
  const { sessions, activeSessionId, addSession, removeSession, setActiveSession } =
    useTerminalStore();

  return (
    <div className="flex items-center border-b border-lb-border-secondary bg-lb-bg-secondary">
      <div className="flex min-w-0 flex-1 overflow-x-auto">
        {sessions.map((session) => {
          const isActive = session.id === activeSessionId;
          return (
            <button
              key={session.id}
              onClick={() => setActiveSession(session.id)}
              className={`group flex shrink-0 items-center gap-1.5 border-r border-lb-border-secondary px-3 py-1.5 text-xs font-medium transition-colors ${
                isActive
                  ? "bg-lb-bg-primary text-lb-text-primary"
                  : "bg-lb-bg-secondary text-lb-text-secondary hover:bg-lb-bg-tertiary"
              }`}
            >
              <Terminal size={12} className="shrink-0 text-lb-text-secondary" />
              <span className="truncate">{session.label}</span>
              <span
                className={`inline-block h-1.5 w-1.5 shrink-0 rounded-full ${
                  session.connected
                    ? "bg-lb-state-success"
                    : "bg-lb-text-muted"
                }`}
              />
              <span
                role="button"
                onClick={(e) => {
                  e.stopPropagation();
                  removeSession(session.id);
                }}
                className="shrink-0 rounded p-0.5 opacity-0 transition-opacity hover:bg-lb-bg-tertiary group-hover:opacity-100"
              >
                <X size={10} />
              </span>
            </button>
          );
        })}
      </div>
      <button
        onClick={() => addSession()}
        className="shrink-0 px-2 py-1.5 text-lb-text-secondary transition-colors hover:bg-lb-bg-tertiary hover:text-lb-text-primary"
        title="New terminal"
      >
        <Plus size={14} />
      </button>
    </div>
  );
}
