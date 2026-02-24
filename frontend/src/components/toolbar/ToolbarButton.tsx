import type { LucideIcon } from "lucide-react";
import { Tooltip } from "../shared/Tooltip";

interface ToolbarButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  icon: LucideIcon;
  label: string;
  active?: boolean;
}

export function ToolbarButton({ icon: Icon, label, active, className = "", ...props }: ToolbarButtonProps) {
  return (
    <Tooltip content={label}>
      <button
        aria-label={label}
        className={`inline-flex items-center justify-center rounded p-1.5 text-df-text-secondary transition-colors hover:bg-df-bg-hover hover:text-df-text-primary disabled:opacity-40 disabled:cursor-not-allowed ${active ? "bg-df-bg-active text-df-accent-primary" : ""} ${className}`}
        {...props}
      >
        <Icon size={16} />
      </button>
    </Tooltip>
  );
}
