import { Separator } from "react-resizable-panels";
import { ArrowLeftRight } from "lucide-react";
import { useUiStore } from "../../stores/uiStore";

export function PaneHandle() {
  const togglePaneOrder = useUiStore((s) => s.togglePaneOrder);

  return (
    <Separator className="group relative flex w-1.5 items-center justify-center bg-lb-border-secondary transition-colors hover:bg-lb-accent-primary/30">
      <button
        onClick={togglePaneOrder}
        className="absolute z-10 rounded bg-lb-bg-elevated p-1 opacity-0 shadow transition-opacity group-hover:opacity-100 hover:bg-lb-bg-hover"
        title="Swap panes"
      >
        <ArrowLeftRight size={12} className="text-lb-text-secondary" />
      </button>
    </Separator>
  );
}
