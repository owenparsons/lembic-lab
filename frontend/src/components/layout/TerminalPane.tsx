import { XTerminal } from "../terminal/XTerminal";
import { TerminalHeader } from "../terminal/TerminalHeader";

export function TerminalPane() {
  return (
    <div className="flex h-full flex-col overflow-hidden bg-df-bg-primary">
      <TerminalHeader />
      <div className="flex-1 overflow-hidden">
        <XTerminal />
      </div>
    </div>
  );
}
