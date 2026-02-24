import type { LucideIcon } from "lucide-react";
import { forwardRef } from "react";

interface IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  icon: LucideIcon;
  size?: number;
  label: string;
}

export const IconButton = forwardRef<HTMLButtonElement, IconButtonProps>(
  ({ icon: Icon, size = 16, label, className = "", ...props }, ref) => {
    return (
      <button
        ref={ref}
        aria-label={label}
        title={label}
        className={`inline-flex items-center justify-center rounded p-1.5 text-df-text-secondary transition-colors hover:bg-df-bg-hover hover:text-df-text-primary disabled:opacity-40 disabled:cursor-not-allowed ${className}`}
        {...props}
      >
        <Icon size={size} />
      </button>
    );
  },
);

IconButton.displayName = "IconButton";
