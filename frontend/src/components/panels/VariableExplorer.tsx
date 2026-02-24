import { useEffect } from "react";
import { X, RefreshCw, Database } from "lucide-react";
import { useVariableStore } from "../../stores/variableStore";
import { useUiStore } from "../../stores/uiStore";
import { useProfileStore } from "../../stores/profileStore";
import { formatBytes } from "../../utils/formatters";

export function VariableExplorer() {
  const variables = useVariableStore((s) => s.variables);
  const loading = useVariableStore((s) => s.loading);
  const refresh = useVariableStore((s) => s.refresh);
  const toggleVariableExplorer = useUiStore((s) => s.toggleVariableExplorer);
  const loadProfile = useProfileStore((s) => s.loadProfile);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return (
    <div className="flex h-full flex-col border-l border-df-border-primary bg-df-bg-secondary">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-df-border-primary px-3 py-2">
        <div className="flex items-center gap-2">
          <Database size={14} className="text-df-accent-primary" />
          <span className="text-xs font-semibold text-df-text-primary">
            Variables
          </span>
          <span className="text-xs text-df-text-muted">
            ({variables.length})
          </span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => refresh()}
            disabled={loading}
            className="rounded p-1 text-df-text-muted transition-colors hover:bg-df-bg-hover hover:text-df-text-primary disabled:opacity-50"
            title="Refresh"
          >
            <RefreshCw size={13} className={loading ? "animate-spin" : ""} />
          </button>
          <button
            onClick={toggleVariableExplorer}
            className="rounded p-1 text-df-text-muted transition-colors hover:bg-df-bg-hover hover:text-df-text-primary"
            title="Close"
          >
            <X size={13} />
          </button>
        </div>
      </div>

      {/* Variable list */}
      <div className="flex-1 overflow-y-auto">
        {variables.length === 0 ? (
          <div className="px-3 py-4 text-center text-xs text-df-text-muted">
            {loading ? "Loading..." : "No variables in kernel"}
          </div>
        ) : (
          <table className="w-full text-xs">
            <thead className="sticky top-0 bg-df-bg-secondary">
              <tr className="border-b border-df-border-secondary">
                <th className="px-3 py-1.5 text-left font-semibold text-df-text-secondary">
                  Name
                </th>
                <th className="px-3 py-1.5 text-left font-semibold text-df-text-secondary">
                  Type
                </th>
                <th className="px-3 py-1.5 text-left font-semibold text-df-text-secondary">
                  Value
                </th>
              </tr>
            </thead>
            <tbody>
              {variables.map((v) => (
                <tr
                  key={v.name}
                  className="border-b border-df-border-secondary hover:bg-df-bg-hover"
                >
                  <td className="px-3 py-1.5">
                    <button
                      onClick={() => {
                        if (v.var_type === "DataFrame") {
                          loadProfile(v.name);
                        }
                      }}
                      className={`font-mono font-medium ${
                        v.var_type === "DataFrame"
                          ? "cursor-pointer text-df-accent-primary hover:underline"
                          : "text-df-syntax-variable"
                      }`}
                    >
                      {v.name}
                    </button>
                  </td>
                  <td className="px-3 py-1.5 text-df-syntax-type">
                    {v.var_type}
                    {v.shape && (
                      <span className="ml-1 text-df-text-muted">
                        {v.shape}
                      </span>
                    )}
                  </td>
                  <td className="max-w-[200px] truncate px-3 py-1.5 font-mono text-df-text-primary">
                    {v.preview}
                    {v.size_bytes != null && (
                      <span className="ml-2 text-df-text-muted">
                        ({formatBytes(v.size_bytes)})
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
