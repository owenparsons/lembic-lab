import { ExecutionControls } from "./ExecutionControls";
import { CellOperations } from "./CellOperations";
import { PackageInstall } from "./PackageInstall";
import { UtilityButtons } from "./UtilityButtons";
import { WarningIndicator } from "./WarningIndicator";

export function Toolbar() {
  return (
    <div className="flex items-center gap-2 border-b border-lb-border-secondary bg-lb-bg-secondary px-3 py-1.5">
      <ExecutionControls />
      <div className="mx-1 h-4 w-px bg-lb-border-secondary" />
      <CellOperations />
      <div className="flex-1" />
      <PackageInstall />
      <WarningIndicator />
      <UtilityButtons />
    </div>
  );
}
