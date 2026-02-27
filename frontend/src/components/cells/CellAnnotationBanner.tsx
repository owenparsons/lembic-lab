import { AlertCircle, CheckCircle, Info, AlertTriangle } from "lucide-react";
import type { CellAnnotation } from "../../types/cell";

const STYLE_CONFIG = {
  info: {
    icon: Info,
    bg: "bg-blue-500/10",
    border: "border-blue-500/30",
    text: "text-blue-300",
  },
  warning: {
    icon: AlertTriangle,
    bg: "bg-amber-500/10",
    border: "border-amber-500/30",
    text: "text-amber-300",
  },
  success: {
    icon: CheckCircle,
    bg: "bg-emerald-500/10",
    border: "border-emerald-500/30",
    text: "text-emerald-300",
  },
  error: {
    icon: AlertCircle,
    bg: "bg-red-500/10",
    border: "border-red-500/30",
    text: "text-red-300",
  },
} as const;

export function CellAnnotationBanner({ annotation }: { annotation: CellAnnotation }) {
  const config = STYLE_CONFIG[annotation.style] || STYLE_CONFIG.info;
  const Icon = config.icon;

  return (
    <div
      className={`flex items-center gap-2 rounded-t-md border-b px-3 py-1.5 ${config.bg} ${config.border} ${config.text}`}
    >
      <Icon size={13} />
      <span className="text-xs">{annotation.text}</span>
    </div>
  );
}
