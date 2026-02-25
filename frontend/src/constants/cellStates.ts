import type { CellState } from "../types/cell";

export interface CellStateConfig {
  label: string;
  color: string;
  icon: string; // lucide-react icon name
}

export const CELL_STATE_CONFIG: Record<CellState, CellStateConfig> = {
  idle: { label: "Not run", color: "var(--lb-state-idle)", icon: "Circle" },
  running: { label: "Running", color: "var(--lb-state-running)", icon: "Loader" },
  success: { label: "Success", color: "var(--lb-state-success)", icon: "CheckCircle" },
  error: { label: "Error", color: "var(--lb-state-error)", icon: "XCircle" },
  stale: { label: "Stale", color: "var(--lb-state-stale)", icon: "AlertCircle" },
  stale_upstream: {
    label: "Upstream changed",
    color: "var(--lb-state-stale-upstream)",
    icon: "AlertTriangle",
  },
};
