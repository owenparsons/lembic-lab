import type { CellState } from "../types/cell";

export interface CellStateConfig {
  label: string;
  color: string;
  icon: string; // lucide-react icon name
}

export const CELL_STATE_CONFIG: Record<CellState, CellStateConfig> = {
  idle: { label: "Not run", color: "var(--df-state-idle)", icon: "Circle" },
  running: { label: "Running", color: "var(--df-state-running)", icon: "Loader" },
  success: { label: "Success", color: "var(--df-state-success)", icon: "CheckCircle" },
  error: { label: "Error", color: "var(--df-state-error)", icon: "XCircle" },
  stale: { label: "Stale", color: "var(--df-state-stale)", icon: "AlertCircle" },
  stale_upstream: {
    label: "Upstream changed",
    color: "var(--df-state-stale-upstream)",
    icon: "AlertTriangle",
  },
};
