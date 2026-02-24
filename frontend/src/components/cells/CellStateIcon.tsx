import {
  Circle,
  Loader,
  CheckCircle,
  XCircle,
  AlertCircle,
  AlertTriangle,
  type LucideIcon,
} from "lucide-react";
import type { CellState } from "../../types/cell";
import { CELL_STATE_CONFIG } from "../../constants/cellStates";

const ICON_MAP: Record<string, LucideIcon> = {
  Circle,
  Loader,
  CheckCircle,
  XCircle,
  AlertCircle,
  AlertTriangle,
};

interface CellStateIconProps {
  state: CellState;
  size?: number;
}

export function CellStateIcon({ state, size = 14 }: CellStateIconProps) {
  const config = CELL_STATE_CONFIG[state];
  const Icon = ICON_MAP[config.icon] ?? Circle;

  return (
    <Icon
      size={size}
      style={{ color: config.color }}
      className={state === "running" ? "animate-spin" : ""}
    />
  );
}
