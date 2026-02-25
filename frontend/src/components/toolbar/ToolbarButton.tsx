import type { LucideIcon } from "lucide-react";
import { Tooltip } from "../shared/Tooltip";

interface ToolbarButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  icon: LucideIcon;
  label: string;
  active?: boolean;
}

export function ToolbarButton({ icon: Icon, label, active, className = "", ...props }: ToolbarButtonProps) {
  return (
    <Tooltip content={label} position="bottom">
      <button
        aria-label={label}
        className={`inline-flex items-center justify-center rounded p-1.5 text-lb-text-secondary transition-colors hover:bg-lb-bg-hover hover:text-lb-text-primary disabled:opacity-40 disabled:cursor-not-allowed ${active ? "bg-lb-bg-active text-lb-accent-primary" : ""} ${className}`}
        {...props}
      >
        <Icon size={16} />
      </button>
    </Tooltip>
  );
}
