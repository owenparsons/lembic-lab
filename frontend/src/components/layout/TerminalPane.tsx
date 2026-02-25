import { useRef } from "react";
import { XTerminal } from "../terminal/XTerminal";
import { TerminalHeader } from "../terminal/TerminalHeader";
import { InjectionBar } from "../terminal/InjectionBar";

export function TerminalPane() {
  const sendToTerminalRef = useRef<((message: string) => void) | null>(null);

  return (
    <div className="flex h-full flex-col overflow-hidden bg-lb-bg-primary">
      <TerminalHeader />
      <div className="flex-1 overflow-hidden">
        <XTerminal onSendRef={sendToTerminalRef} />
      </div>
      <InjectionBar
        onSend={(message) => sendToTerminalRef.current?.(message)}
      />
    </div>
  );
}
