import { useEffect, useRef, useCallback } from "react";
import { XTerminal } from "../terminal/XTerminal";
import { TerminalTabBar } from "../terminal/TerminalTabBar";
import { InjectionBar } from "../terminal/InjectionBar";
import { useTerminalStore } from "../../stores/terminalStore";
import { useUiStore } from "../../stores/uiStore";
import { VariableExplorer } from "../panels/VariableExplorer";
import { DependencyGraph } from "../panels/DependencyGraph";
import { DataProfilePanel } from "../panels/DataProfilePanel";

export function TerminalPane() {
  const sessions = useTerminalStore((s) => s.sessions);
  const activeSessionId = useTerminalStore((s) => s.activeSessionId);
  const addSession = useTerminalStore((s) => s.addSession);
  const activeRightTab = useUiStore((s) => s.activeRightTab);

  // Map of session id → send function
  const sendFnsRef = useRef<Map<string, (message: string) => void>>(new Map());

  // Create default session on mount if none exist, with claude auto-started
  useEffect(() => {
    if (useTerminalStore.getState().sessions.length === 0) {
      addSession({ initCommand: "claude" });
    }
  }, []);

  const handleSend = useCallback(
    (message: string) => {
      if (activeSessionId) {
        sendFnsRef.current.get(activeSessionId)?.(message);
      }
    },
    [activeSessionId],
  );

  return (
    <div className="flex h-full flex-col overflow-hidden bg-lb-bg-primary">
      <TerminalTabBar />
      <div className="relative flex-1 overflow-hidden">
        {sessions.map((session) => (
          <div
            key={session.id}
            className="absolute inset-0"
            style={{
              display: session.id === activeRightTab ? "block" : "none",
            }}
          >
            <XTerminal
              sessionId={session.id}
              visible={session.id === activeRightTab}
              initCommand={session.initCommand}
              onSendReady={(sendFn) => {
                sendFnsRef.current.set(session.id, sendFn);
              }}
            />
          </div>
        ))}

        {activeRightTab === "variables" && (
          <div className="absolute inset-0 overflow-hidden">
            <VariableExplorer />
          </div>
        )}
        {activeRightTab === "dependencies" && (
          <div className="absolute inset-0 overflow-hidden">
            <DependencyGraph />
          </div>
        )}
        {activeRightTab === "profile" && (
          <div className="absolute inset-0 overflow-hidden">
            <DataProfilePanel />
          </div>
        )}
      </div>
      <InjectionBar onSend={handleSend} />
    </div>
  );
}
