import { useEffect, useState } from "react";
import { Loader2, Trash2, RefreshCw, FolderOpen } from "lucide-react";
import { useEnvironmentStore } from "../../stores/environmentStore";

export function PackagePanel() {
  const status = useEnvironmentStore((s) => s.status);
  const packages = useEnvironmentStore((s) => s.packages);
  const installing = useEnvironmentStore((s) => s.installing);
  const loadStatus = useEnvironmentStore((s) => s.loadStatus);
  const loadPackages = useEnvironmentStore((s) => s.loadPackages);
  const install = useEnvironmentStore((s) => s.install);
  const uninstall = useEnvironmentStore((s) => s.uninstall);
  const setExternal = useEnvironmentStore((s) => s.setExternal);
  const remove = useEnvironmentStore((s) => s.remove);

  const [installValue, setInstallValue] = useState("");
  const [externalPath, setExternalPath] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    loadStatus();
    loadPackages();
  }, [loadStatus, loadPackages]);

  const handleInstall = async () => {
    const pkgs = installValue
      .split(",")
      .map((p) => p.trim())
      .filter(Boolean);
    if (pkgs.length === 0) return;
    const result = await install(pkgs);
    if (result.success) {
      setInstallValue("");
      setMessage(`Installed ${pkgs.join(", ")}. Run a cell to start the kernel.`);
    } else {
      setMessage("Install failed: " + result.output.slice(0, 200));
    }
    setTimeout(() => setMessage(null), 5000);
  };

  const handleSetExternal = async () => {
    if (!externalPath.trim()) return;
    const result = await setExternal(externalPath.trim());
    if (result.success) {
      setExternalPath("");
      setMessage("External env set. Run a cell to start the kernel.");
    } else {
      setMessage(result.message);
    }
    setTimeout(() => setMessage(null), 5000);
  };

  return (
    <div className="flex h-full flex-col overflow-hidden bg-lb-bg-primary p-3 text-sm text-lb-text-primary">
      {/* Status header */}
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span
            className={`inline-block h-2 w-2 rounded-full ${status?.exists ? "bg-lb-state-success" : "bg-lb-text-muted"}`}
          />
          <span className="font-medium">
            {status?.exists
              ? `Python ${status.python_version ?? ""}${status.external ? " (external)" : ""}`
              : "No environment"}
          </span>
          {status?.exists && (
            <span className="text-xs text-lb-text-muted">
              {status.package_count} packages
            </span>
          )}
        </div>
        <button
          onClick={() => {
            loadStatus();
            loadPackages();
          }}
          className="rounded p-1 text-lb-text-secondary hover:bg-lb-bg-hover"
          title="Refresh"
        >
          <RefreshCw size={14} />
        </button>
      </div>

      {/* Install input */}
      <div className="mb-3">
        <div className="flex gap-1.5">
          <input
            type="text"
            value={installValue}
            onChange={(e) => setInstallValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !installing) handleInstall();
            }}
            placeholder="Package names (comma-separated)..."
            disabled={installing}
            className="flex-1 rounded border border-lb-border-secondary bg-lb-bg-secondary px-2 py-1 text-xs text-lb-text-primary placeholder:text-lb-text-muted focus:border-lb-accent-primary focus:outline-none disabled:opacity-50"
          />
          <button
            onClick={handleInstall}
            disabled={installing || !installValue.trim()}
            className="rounded bg-lb-accent-primary px-2 py-1 text-xs text-white hover:opacity-90 disabled:opacity-50"
          >
            {installing ? (
              <Loader2 size={12} className="animate-spin" />
            ) : (
              "Install"
            )}
          </button>
        </div>
      </div>

      {/* Message */}
      {message && (
        <div className="mb-2 rounded bg-lb-bg-secondary px-2 py-1 text-xs text-lb-text-secondary">
          {message}
        </div>
      )}

      {/* Package list */}
      <div className="flex-1 overflow-y-auto">
        {packages.length === 0 ? (
          <div className="py-4 text-center text-xs text-lb-text-muted">
            {status?.exists
              ? "No packages installed"
              : "Install a package to create the environment"}
          </div>
        ) : (
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-lb-border-secondary text-left text-lb-text-muted">
                <th className="pb-1 font-medium">Package</th>
                <th className="pb-1 font-medium">Version</th>
                <th className="pb-1 w-8" />
              </tr>
            </thead>
            <tbody>
              {packages.map((pkg) => (
                <tr
                  key={pkg.name}
                  className="border-b border-lb-border-secondary/50 hover:bg-lb-bg-hover"
                >
                  <td className="py-1 font-mono">{pkg.name}</td>
                  <td className="py-1 text-lb-text-secondary">{pkg.version}</td>
                  <td className="py-1">
                    <button
                      onClick={() => uninstall([pkg.name])}
                      className="rounded p-0.5 text-lb-text-muted hover:text-lb-state-error"
                      title={`Uninstall ${pkg.name}`}
                    >
                      <Trash2 size={12} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* External env / remove section */}
      <div className="mt-3 border-t border-lb-border-secondary pt-3">
        <div className="mb-2 flex items-center gap-1.5">
          <FolderOpen size={12} className="text-lb-text-muted" />
          <span className="text-xs text-lb-text-muted">External environment</span>
        </div>
        <div className="flex gap-1.5">
          <input
            type="text"
            value={externalPath}
            onChange={(e) => setExternalPath(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleSetExternal();
            }}
            placeholder="/path/to/venv"
            className="flex-1 rounded border border-lb-border-secondary bg-lb-bg-secondary px-2 py-1 text-xs text-lb-text-primary placeholder:text-lb-text-muted focus:border-lb-accent-primary focus:outline-none"
          />
          <button
            onClick={handleSetExternal}
            disabled={!externalPath.trim()}
            className="rounded border border-lb-border-secondary px-2 py-1 text-xs text-lb-text-secondary hover:bg-lb-bg-hover disabled:opacity-50"
          >
            Use
          </button>
        </div>
        {status?.exists && !status.external && (
          <button
            onClick={remove}
            className="mt-2 text-xs text-lb-state-error hover:underline"
          >
            Remove environment
          </button>
        )}
      </div>
    </div>
  );
}
