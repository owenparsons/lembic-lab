import { Separator } from "react-resizable-panels";
import { ArrowLeftRight } from "lucide-react";
import { useUiStore } from "../../stores/uiStore";

export function PaneHandle() {
  const togglePaneOrder = useUiStore((s) => s.togglePaneOrder);

  return (
    <Separator className="group relative flex w-1.5 items-center justify-center bg-df-border-secondary transition-colors hover:bg-df-accent-primary/30">
      <button
        onClick={togglePaneOrder}
        className="absolute z-10 rounded bg-df-bg-elevated p-1 opacity-0 shadow transition-opacity group-hover:opacity-100 hover:bg-df-bg-hover"
        title="Swap panes"
      >
        <ArrowLeftRight size={12} className="text-df-text-secondary" />
      </button>
    </Separator>
  );
}
