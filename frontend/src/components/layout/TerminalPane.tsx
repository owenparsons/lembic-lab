import { useEffect, useRef, useCallback } from "react";
import { XTerminal } from "../terminal/XTerminal";
import { TerminalTabBar } from "../terminal/TerminalTabBar";
import { InjectionBar } from "../terminal/InjectionBar";
import { useTerminalStore } from "../../stores/terminalStore";
import { useUiStore } from "../../stores/uiStore";
import { VariableExplorer } from "../panels/VariableExplorer";
import { DependencyGraph } from "../panels/DependencyGraph";
import { DataProfilePanel } from "../panels/DataProfilePanel";
import { PackagePanel } from "../panels/PackagePanel";

export function TerminalPane() {
  const sessions = useTerminalStore((s) => s.sessions);
  const activeSessionId = useTerminalStore((s) => s.activeSessionId);
  const addSession = useTerminalStore((s) => s.addSession);
  const activePanelTab = useUiStore((s) => s.activePanelTab);

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
        {sessions.map((session) => {
          const isVisible =
            session.id === activeSessionId && !activePanelTab;
          return (
            <div
              key={session.id}
              className="absolute inset-0"
              style={{
                visibility: isVisible ? "visible" : "hidden",
              }}
            >
              <XTerminal
                sessionId={session.id}
                visible={isVisible}
                initCommand={session.initCommand}
                onSendReady={(sendFn) => {
                  sendFnsRef.current.set(session.id, sendFn);
                }}
              />
            </div>
          );
        })}

        {activePanelTab === "variables" && (
          <div className="absolute inset-0 overflow-hidden">
            <VariableExplorer />
          </div>
        )}
        {activePanelTab === "dependencies" && (
          <div className="absolute inset-0 overflow-hidden">
            <DependencyGraph />
          </div>
        )}
        {activePanelTab === "profile" && (
          <div className="absolute inset-0 overflow-hidden">
            <DataProfilePanel />
          </div>
        )}
        {activePanelTab === "packages" && (
          <div className="absolute inset-0 overflow-hidden">
            <PackagePanel />
          </div>
        )}
      </div>
      <InjectionBar onSend={handleSend} />
    </div>
  );
}
