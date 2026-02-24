import type { ReactNode } from "react";

interface NotebookPaneProps {
  children: ReactNode;
}

export function NotebookPane({ children }: NotebookPaneProps) {
  return (
    <div className="flex h-full flex-col overflow-hidden bg-df-bg-primary">
      {children}
    </div>
  );
}
