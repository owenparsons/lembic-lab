import { useEffect, useRef } from "react";

interface ContextMenuItem {
  label: string;
  onClick: () => void;
  disabled?: boolean;
  separator?: boolean;
}

interface ContextMenuProps {
  x: number;
  y: number;
  items: ContextMenuItem[];
  onClose: () => void;
}

export function ContextMenu({ x, y, items, onClose }: ContextMenuProps) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        onClose();
      }
    };
    const keyHandler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("mousedown", handler);
    document.addEventListener("keydown", keyHandler);
    return () => {
      document.removeEventListener("mousedown", handler);
      document.removeEventListener("keydown", keyHandler);
    };
  }, [onClose]);

  return (
    <div
      ref={ref}
      className="fixed z-50 min-w-[160px] rounded-md border border-df-border-primary bg-df-bg-elevated py-1 shadow-xl"
      style={{ left: x, top: y }}
    >
      {items.map((item, i) =>
        item.separator ? (
          <div key={i} className="my-1 h-px bg-df-border-secondary" />
        ) : (
          <button
            key={i}
            className="w-full px-3 py-1.5 text-left text-sm text-df-text-primary hover:bg-df-bg-hover disabled:opacity-40 disabled:cursor-not-allowed"
            onClick={() => {
              item.onClick();
              onClose();
            }}
            disabled={item.disabled}
          >
            {item.label}
          </button>
        ),
      )}
    </div>
  );
}
